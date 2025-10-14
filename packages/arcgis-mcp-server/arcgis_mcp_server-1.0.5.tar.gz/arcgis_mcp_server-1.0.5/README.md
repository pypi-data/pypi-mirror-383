\# ArcGIS MCP Server



\[!\[PyPI Version](https://img.shields.io/pypi/v/arcgis-mcp-server.svg)](https://pypi.org/project/arcgis-mcp-server/)

\[!\[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



An intelligent AI agent tool for searching content within ArcGIS Portal and ArcGIS Online, designed to be used with AI assistants like GitHub Copilot in VS Code.



This server allows you to use natural language to find items like feature layers, web maps, and other geographic data directly within your development environment.



\## Features ✨



\* \*\*Natural Language Queries\*\*: Search for ArcGIS items using plain English.

\* \*\*Secure Authentication\*\*: Securely connects to your ArcGIS organization using a one-time credential prompt.

\* \*\*Seamless VS Code Integration\*\*: Works automatically with the GitHub Copilot `@workspace` agent.

\* \*\*Lightweight and Fast\*\*: Built with a minimal footprint to be quick and responsive.



\## Requirements



Before you begin, ensure you have the following installed:



1\.  \*\*Visual Studio Code\*\*: The code editor.

2\.  \*\*Miniconda/Anaconda\*\*: For managing Python environments.

3\.  \*\*GitHub Copilot Extension\*\*: The AI assistant for VS Code.



\## 🚀 Quickstart: Installation and Usage



Follow these steps to get the ArcGIS MCP Server running in minutes.



\### 1. Installation



First, install the tool into a clean Python environment.



1\.  \*\*Create a Conda Environment\*\*:

&nbsp;   ```bash

&nbsp;   conda create --name arcgis-tool-env python=3.11 -y

&nbsp;   ```



2\.  \*\*Activate the Environment\*\*:

&nbsp;   ```bash

&nbsp;   conda activate arcgis-tool-env

&nbsp;   ```



3\.  \*\*Install the Package from PyPI\*\*:

&nbsp;   ```bash

&nbsp;   pip install arcgis-mcp-server

&nbsp;   ```



\### 2. Configuration in VS Code



Now, tell VS Code to use the environment where you just installed the tool.



1\.  \*\*Open VS Code\*\*.

2\.  Open the \*\*Command Palette\*\* (`Ctrl+Shift+P` or `Cmd+Shift+P`).

3\.  Run the command \*\*`Python: Select Interpreter`\*\*.

4\.  From the list, choose the \*\*`arcgis-tool-env`\*\* Conda environment.



VS Code will now automatically discover and start the server.



\### 3. Usage with Copilot Chat



You can now chat with your ArcGIS organization.



1\.  \*\*Open Copilot Chat\*\* in the sidebar.

2\.  Select the \*\*`@workspace`\*\* agent by typing `@` in the chat box.

3\.  \*\*Ask a Question\*\*: Type a prompt to find data. For example:

&nbsp;   ```

&nbsp;   @workspace find feature layers about roads in my ArcGIS organization

&nbsp;   ```

4\.  \*\*Authenticate\*\*: The first time you run a query, a secure pop-up will appear asking for your \*\*ArcGIS URL, Username, and Password\*\*. Enter your credentials to connect.

5\.  \*\*Get Your Results\*\*: Copilot will use the tool and display the items it found.







\## For Developers



If you wish to contribute or run the server from the source code for development:



1\.  \*\*Clone the repository\*\*:

&nbsp;   ```bash

&nbsp;   git clone \[https://github.com/esrisaudiarabia/esrisaudiarabia-mcp.git](https://github.com/esrisaudiarabia/esrisaudiarabia-mcp.git)

&nbsp;   cd esrisaudiarabia-mcp

&nbsp;   ```

2\.  \*\*Create and activate the Conda environment\*\* as shown in the installation steps.

3\.  \*\*Install in editable mode\*\*: This links the installed package to your source code.

&nbsp;   ```bash

&nbsp;   pip install -e .

&nbsp;   ```

4\.  You can now make changes to `arcgis\_mcp.py` and test them by reloading the VS Code window.



\## License



This project is licensed under the MIT License. See the `LICENSE` file for details.



---

mcp-name: io.github.esrisaudiarabia/arcgis-mcp-server

