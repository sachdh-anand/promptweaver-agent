# Prompt: Build A Production-Ready, Fully Automated Crewai Project That Converts All Pdfs Inside A Source_Pdfs/ Folder Into Cleaned And Reviewed Markdown Files Using Microsoft'S Markitdown Tool (Https://Github.Com/Microsoft/Markitdown). The Project Should Follow A Modular Architecture And Use A Sequential Multi-Agent System Where: (1) A Pdf Watcher Agent Detects New Files, (2) A Pdf Converter Agent Uses Markitdown To Convert Them To Markdown, (3) A Markdown Cleaner Agent Reviews And Formats The Content, And (4) A Markdown Mover Agent Saves The Final .Md File Into A Converted_Markdown/ Folder. Also, Include An Additional Qa Agent That Verifies Markdown Structure And Readability Using A Language Model. The Project Should Follow This Folder Structure: Markitflow/ ├── Pyproject.Toml ├── Readme.Md ├── Run.Ps1 ├── Run.Sh ├── Uv.Lock ├── Source_Pdfs/ ├── Converted_Markdown/ ├── Logs/ ├── Src/ │   ├── Crew.Py │   ├── Main.Py │   ├── Tools/ │   │   └── Markitdown_Tool.Py │   └── Utils/ │       ├── File_Utils.Py │       └── Output_Logger.Py. Also Create An Intuitive, Modern, Attractive And Impressive Frontend In App.Py Using Streamlit With File Upload, Conversion Progress, And Markdown Preview. The User Should Be Able To Drag And Drop Pdfs Into The Ui, View Markdown Results In Real-Time, And Download The Cleaned Files. The Ui Must Be World-Class And Feel Like A Premium Experience. The Output Must Include All Agent And Task Definitions (Yaml Or Python), Working Code For The Frontend, And A Complete Cli Runner. Do Not Add Framework Breakdowns In The Final Output—Only The Working Solution.

**

**CrewAI Project Prompt: "MarkitFlow PDF-to-Markdown Automation Suite"**

**Objective**  
Develop a production-grade CrewAI system that automates PDF-to-Markdown conversion using Microsoft's markitdown tool, featuring a multi-agent workflow, modular architecture, and a premium Streamlit frontend. The solution must include:  
1. **Sequential Agent Workflow**:  
   - **PDF Watcher Agent**: Monitors `source_pdfs/` for new files (inotify/threading).  
   - **PDF Converter Agent**: Executes markitdown CLI conversion with error fallbacks.  
   - **Markdown Cleaner Agent**: Applies regex formatting (headers, lists, code blocks).  
   - **Markdown Mover Agent**: Saves files to `converted_markdown/` with metadata.  
   - **QA Agent**: Validates Markdown structure using GPT-4 Turbo (API call + regex checks).  
2. **Folder Structure Compliance**:  
   ```  
   markitflow/  
   ├── pyproject.toml (with deps: crewai, markitdown, streamlit, python-dotenv)  
   ├── run.ps1 & run.sh (CLI runners with --watch/--single flags)  
   ├── src/  
   │   ├── crew.py (Agent/Task definitions via YAML)  
   │   ├── main.py (Crew orchestration)  
   │   ├── tools/markitdown_tool.py (subprocess wrapper + error logging)  
   │   └── utils/file_utils.py (path sanitization, batch processing)  
   ```  
3. **Streamlit Frontend**:  
   - Drag-and-drop zone with `st.file_uploader` (accepts multiple PDFs).  
   - Real-time conversion progress using `st.progress` + `st.status`.  
   - Dual-pane preview: Original PDF (via pdf2image) ↔ Cleaned Markdown.  
   - Download button with custom filename (e.g., `{original_name}_converted.md`).  
   - Modern UI: Dark theme, animated transitions (Lottie), and toast notifications.  

**Technical Requirements**  
- **Error Handling**: Retry failed conversions 3x with exponential backoff.  
- **Logging**: JSON logs in `logs/` with UUID per conversion job.  
- **QA Checks**:  
  ```python  
  def validate_markdown(content):  
      # GPT-4 call: "Rate readability 1-10 and flag Markdown errors"  
      # Regex checks for broken links, headers without content, etc.  
  ```  
- **Performance**: Async processing for ≥10 concurrent PDFs.  

**Deliverables**  
1. Complete Python code for all agents, tools, and utils (no placeholders).  
2. Streamlit `app.py` with mobile-responsive design.  
3. YAML task definitions for CrewAI (timeouts, error handlers).  
4. Pre-configured CLI runners supporting `--watch` (daemon mode) and `--single` (one-off).  

**Example Snippet for PDF Converter Agent**  
```python  
# src/tools/markitdown_tool.py  
def convert_pdf_to_markdown(input_path):  
    output_dir = os.path.join("converted_markdown", str(uuid.uuid4()))  
    cmd = f"markitdown convert {input_path} -o {output_dir} --strict"  
    try:  
        subprocess.run(cmd, check=True, shell=True, timeout=120)  
        return output_dir  
    except subprocess.CalledProcessError as e:  
        log_error(f"Conversion failed: {e}")  
        raise  
```  

**Frontend Design Specs**  
- **Color Scheme**: Slate-900 background, Emerald-400 accents.  
- **Animations**: Spinners on upload, confetti on successful conversion.  
- **Security**: File hash verification to prevent duplicate processing.  

**Validation**  
- Integration tests for 100+ page PDFs with tables/images.  
- Load testing for 50 concurrent users.  

🧠 **Prompt Engineering** + 🤖 **AI Architecture** + 🎨 **UX Design**  

**Feedback Request**  
Does this structure align with your vision? Should I refine any components (e.g., QA Agent implementation, frontend features)?
