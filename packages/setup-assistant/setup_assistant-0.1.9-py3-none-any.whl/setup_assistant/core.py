import os
import re
import subprocess
import platform
import logging
from google import genai
from google.genai import types
import httpx
import pathlib
import io
from setup_assistant.helpers import *
import webbrowser
import markdown
from pathlib import Path
import PyPDF2


class SetupAssistant:
    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = getAPIKey("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Google API key not found. Set GOOGLE_API_KEY in your environment."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model

        self.os_name = platform.system().lower()
        if self.os_name == "darwin":
            self.os_name = "macos"

        self.shell_rc_file = (
            os.path.expanduser("~/.zshrc")
            if self.os_name == "macos"
            else os.path.expanduser("~/.bashrc")
        )
        logging.info(f"Running on {self.os_name}, using {self.shell_rc_file}.")

        self.config = types.GenerateContentConfig(
            system_instruction=getSystemInstructions(self.os_name)
        )
        self.chat = self.client.chats.create(model=self.model, config=self.config)
        
    


    def ask_ai(self, query: str) -> str:
        try:
            response = self.chat.send_message(query)
            return response.candidates[0].content.parts[0].text
        except Exception as e:
            logging.error(f"AI request failed: {e}")
            return ""

    def ask_ai_throughDocument(self, url=None, path=None, useFileAPI=True):
        prompt = "Read the content and figure out the steps that need to be carried out to complete the process mentioned in the content."

        if url and path:
            print("Both URL and path are provided. Prioritizing URL for the process.")
            path = ""

        document_text = None

        if url:
            if "docs.google.com/document" in url:
                file_id = extract_drive_file_id(url)
                pdf_path = download_google_doc_as_pdf(file_id, "downloaded_doc.pdf")
                filePath = pathlib.Path(pdf_path)
                if filePath.suffix.lower() == ".pdf":
                    document_text = self.read_pdf_text(filePath)
                else:
                    document_text = read_document(filePath)

            elif "drive.google.com" in url:
                file_id = extract_drive_file_id(url)
                local_file = download_drive_file(file_id, "downloaded_file")
                filePath = pathlib.Path(local_file)
                if filePath.suffix.lower() == ".pdf":
                    document_text = self.read_pdf_text(filePath)
                else:
                    document_text = read_document(filePath)

        elif path:
            filePath = pathlib.Path(path)
            fileExtension = filePath.suffix.lower()

            if fileExtension == ".pdf":
                document_text = self.read_pdf_text(filePath)
            else:
                document_text = read_document(filePath)

        if not document_text:
            raise ValueError("No valid document found to process.")

        response = self.ask_ai(f"{document_text}\n{prompt}")
        return parse_ai_response(response)


    def execute_commands(
        self,
        commands: list[str],
        results: list,
        nextPrompt,
        max_retries: int = 2,
        depth: int = 0,
        max_depth: int = 3,
    ):

        if depth >= max_depth:
            logging.error("Max depth reached. Stopping further execution.")
            return results

        def run_single_command(cmd: str):
            """
            Execute a (possibly multi-line) shell command in a running shell subprocess.
            Supports full shell syntax: if/else, loops, here-docs, etc.
            """
            MARKER = "__CMD_DONE__"

            wrapped_cmd = f"""
                                {cmd}
                                echo {MARKER} $?
                                """

            self.proc.stdin.write(wrapped_cmd + "\n")
            self.proc.stdin.flush()

            stdout_lines = []
            while True:
                line = self.proc.stdout.readline()
                if line == "":
                    break

                line = line.rstrip("\n")

                if line.startswith(MARKER):
                    parts = line.split()
                    exit_code = int(parts[1]) if len(parts) > 1 else 1
                    return "\n".join(stdout_lines), exit_code

                stdout_lines.append(line)

            return "\n".join(stdout_lines), -1

        for cmd in commands:
            try:
                if "sudo" in cmd:
                    logging.warning(f"Skipping command '{cmd}' (requires sudo).")
                    results.append(
                        {
                            "command": cmd,
                            "status": "skipped",
                            "reason": "requires sudo privileges",
                        }
                    )
                    continue

                stdout, exit_code = run_single_command(cmd)

                if exit_code == 0:
                    logging.info(f"{cmd}\n{stdout}")
                    results.append(
                        {"command": cmd, "status": "success", "output": stdout}
                    )

                    if (
                        nextPrompt
                        and nextPrompt.strip()
                        and nextPrompt != getattr(self, "last_prompt")
                    ):
                        self.last_prompt = nextPrompt
                        nextStepsResponse = self.ask_ai(
                            f"{nextPrompt}\nPrevious Command response: {stdout}"
                        )

                        logging.info(
                            "--- Next Steps Response ---\n" + nextStepsResponse
                        )
                        nextSteps = parse_ai_response(nextStepsResponse)

                        for step in nextSteps:
                            logging.info(f"Executing the step: {step['instruction']}")
                            new_cmds = strip_commands(step["instruction"])
                            newPrompt = step["prompt"][0] if step.get("prompt") else ""
                            self.execute_commands(
                                new_cmds,
                                results,
                                newPrompt,
                                max_retries,
                                depth + 1,
                                max_depth,
                            )
                    else:
                        logging.info("No new prompt. Ending chain here.")

                else:
                    raise subprocess.CalledProcessError(exit_code, cmd, stdout)

            except subprocess.CalledProcessError as e:
                logging.error(f"Error: {cmd}\n{e.output}")
                results.append({"command": cmd, "status": "error", "stderr": e.output})

                if max_retries > 0:
                    fix = self.ask_ai(
                        f"Command failed: {cmd}\nError: {e.output}\n"
                        f"User reports running on {self.os_name}. "
                        "Please suggest a corrected step. "
                        "Be concise and provide a single command if possible."
                    )
                    new_steps = parse_ai_response(fix)
                    for step in new_steps:
                        new_cmds = strip_commands(step["instruction"])
                        self.execute_commands(
                            new_cmds,
                            results,
                            None,
                            max_retries - 1,
                            depth + 1,
                            max_depth,
                        )

        return results

    def run(self, steps):
        self.last_prompt = steps[0]["instruction"]

        results = []

        self.proc = subprocess.Popen(
            ["/bin/zsh"],  # or /bin/bash
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        try:
            for step in steps:
                logging.info(f"Executing the step: {step['instruction']}")
                commands = strip_commands(step["instruction"])
                nextPrompt = step["prompt"][0] if step["prompt"] else ""
                self.execute_commands(commands, results, nextPrompt)
        finally:
            self.proc.stdin.close()
            self.proc.terminate()

        return results

    def resultsSummaryFile(self, results, fromFileAPI):
        file_path = os.path.abspath("results.html")

        User_output_response = self.ask_ai(
            f"""Final Steps: Take in all the results :{results} for all the steps and provide a detailed output for the user of what happened and 
            what was done until now. Along with that provide if there are any actionable items that the user has to take care of,
            all completing the steps in order for the application or any installed libraries to work as expected.
            """
        )

        summary = []
        for r in results:
            summary.append(
                {
                    "Command": r["command"],
                    "Status": r["status"],
                    "Output / Error": r.get("output")
                    or r.get("stderr")
                    or r.get("reason", ""),
                }
            )
        resultssummary = pd.DataFrame(summary)

        html_sections = []
        html_sections.append("<h2>Execution Results</h2>")
        html_sections.append(
            resultssummary.to_html(classes="table table-striped", border=0)
        )

        if User_output_response:
            html_sections.append(markdown.markdown(User_output_response))

        full_html = f"""
        <html>
            <head>
                <title>Setup Assistant Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .table {{ border-collapse: collapse; width: 100%; }}
                    .table th, .table td {{ border: 1px solid #ddd; padding: 8px; }}
                    .table th {{ background-color: #f4f4f4; }}
                </style>
            </head>
            <body>
                {''.join(html_sections)}
            </body>
        </html>
        """

        if fromFileAPI:
            return User_output_response

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        webbrowser.open(f"file://{file_path}")

        return file_path
    
    
    def read_pdf_text(self,file_path: Path) -> str:
            """
            Extract text from a PDF file.

            Args:
                file_path (Path or str): Path to the PDF file.

            Returns:
                str: The extracted text from all pages of the PDF.
            """
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text