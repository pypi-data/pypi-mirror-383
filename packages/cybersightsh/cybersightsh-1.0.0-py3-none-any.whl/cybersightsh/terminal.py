import os
import subprocess
from colorama import Fore, Style, init
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

init(autoreset=True)

GUIDE_TOPICS = [
    "Getting Started",
    "Automated Recon",
    "Security Tools List",
    "Pentest Workflow",
    "FAQ",
    "Exit Guide"
]

CYBERSIGHT_GUIDE = {
    "Getting Started": [
        ("What do you want to learn about CyberSight?", [
            "Features and Benefits",
            "Installation Instructions",
            "Supported Platforms",
            "Go Back"
        ]),
    ],
    "Automated Recon": [
        ("Which recon feature?", [
            "Subdomain Discovery",
            "Vulnerability Scanning",
            "Single-click Recon Pipeline",
            "Go Back"
        ]),
    ],
    "Security Tools List": [
        ("Select a tool to view details:", [
            "Subfinder",
            "Amass",
            "Nmap",
            "Nuclei",
            "Back"
        ]),
    ],
    "Pentest Workflow": [
        ("What workflow do you need help with?", [
            "Step-by-step Scan",
            "Report Generation",
            "Automated Scheduling",
            "Go Back"
        ]),
    ],
    "FAQ": [
        ("Choose a topic:", [
            "Troubleshooting",
            "Best Practices",
            "Contact Support",
            "Go Back"
        ])
    ]
}

class CyberSightGuideTerminal:
    def __init__(self):
        self.session = PromptSession()
        self.topic_completer = WordCompleter(GUIDE_TOPICS, ignore_case=True)

    def run(self):
        print(Fore.CYAN + "🛡️ Welcome to CyberSight Interactive Guide!")
        print(Fore.YELLOW + "Topic for assistance are upto now available are GUIDE TOPICS: "+ Fore.GREEN + "1.Getting Started, 2.Automated Recon, 3.Security Tools List, 4.Pentest Workflow, 5.FAQ")
        print(Fore.YELLOW + "Type or select a guide topic (or 'Exit Guide' to quit).\n")

        while True:
            try:
                topic = self.session.prompt(
                    f"{Fore.GREEN}Guide Menu {Fore.WHITE}>> ",
                    completer=self.topic_completer
                ).strip()
                if not topic:
                    continue

                if topic.lower() == "exit guide":
                    print(Fore.CYAN + "Goodbye from CyberSight Guide 👋")
                    break
                if topic not in CYBERSIGHT_GUIDE:
                    print(Fore.RED + "❌ Invalid topic. Please choose from the provided options.")
                    continue

                self.interactive_topic(topic)
            except KeyboardInterrupt:
                print("\n" + Fore.YELLOW + "Type 'Exit Guide' to quit.")
            except EOFError:
                break

    def interactive_topic(self, topic):
        questions = CYBERSIGHT_GUIDE.get(topic, [])
        for question, options in questions:
            print(Fore.LIGHTCYAN_EX + "\n" + question)
            for idx, opt in enumerate(options, 1):
                print(Fore.YELLOW + f"  {idx}. {opt}")

            # Option input and validation
            while True:
                choice = self.session.prompt(
                    Fore.GREEN + "Select an option [number]: "
                ).strip()
                if not choice.isdigit() or int(choice) < 1 or int(choice) > len(options):
                    print(Fore.RED + "Select a valid number from above.")
                    continue

                selected = options[int(choice)-1]
                if selected in ["Go Back", "Back"]:
                    print(Fore.CYAN + "Returning to Guide Menu...\n")
                    return
                self.show_help(topic, selected)
                # Optional: break after showing; you may let user return instead
                break

    def show_help(self, topic, option):
        # Example responses - you should expand these with real docs/help!
        print(Fore.GREEN + f"\nHelp for: {topic} >> {option}")
        help_responses = {
            
            "Features and Benefits": (
                "CyberSight automates all major reconnaissance tasks required in modern security testing. "
                "It seamlessly integrates widely-used tools such as Subfinder, Amass, Nmap, and Nuclei, allowing "
                "security professionals to perform thorough asset discovery, vulnerability scanning, and reporting "
                "all within one platform. The automation saves time, reduces manual errors, and generates comprehensive, "
                "structured reports ideal for pentesting and security audits."
            ),

            "Installation Instructions": (
                "To install CyberSight, ensure you have Python 3.8 or higher installed on your machine. Then, run the command:\n\n"
                "  pip install cybersight\n\n"
                "This will download and install CyberSight along with its required dependencies. For usage on Windows, "
                "WSL (Windows Subsystem for Linux) is recommended to ensure compatibility. If you encounter any installation issues, "
                "refer to the troubleshooting section or contact support."
            ),

            "Supported Platforms": (
                "CyberSight is designed to be cross-platform and is officially supported on Linux, macOS, and Windows (via WSL). "
                "On Linux and macOS, it runs natively with full compatibility. For Windows users, it is highly recommended to use "
                "Windows Subsystem for Linux (WSL) to run CyberSight smoothly with access to native Linux tools and scripts."
            ),

            "Subdomain Discovery": (
                "CyberSight uses industry-standard tools Subfinder and Amass to perform rapid and extensive subdomain enumeration. "
                "These tools leverage multiple data sources including public DNS records, certificate transparency logs, and search engines "
                "to discover associated domains and subdomains under a target domain. This helps in mapping the attack surface comprehensively."
            ),

            "Vulnerability Scanning": (
                "CyberSight runs powerful vulnerability scans using Nuclei templates against the discovered assets. Nuclei is a fast, "
                "template-based vulnerability scanner that detects common misconfigurations, known CVEs, outdated software, and more. "
                "Reports highlight potential security weaknesses for further analysis and remediation."
            ),

            "Single-click Recon Pipeline": (
                "The single-click recon pipeline allows users to initiate a full reconnaissance process with a single command. "
                "It chains together multiple tools: Amass and Subfinder for subdomain enumeration, Nmap for port scanning, and Nuclei for vulnerability detection. "
                "This pipeline automates the entire workflow, delivering comprehensive asset discovery and vulnerability assessment results efficiently."
            ),

            "Step-by-step Scan": (
                "Initiate scans by selecting target domains or IP ranges. Monitor scan progress live through the dashboard interface, "
                "which visualizes ongoing enumeration, port scans, and vulnerability detection. Stepwise control allows pausing or canceling scans as needed, "
                "providing flexibility during engagements."
            ),

            "Report Generation": (
                "CyberSight compiles scan results into detailed reports exportable in PDF and CSV formats. These reports include discovered assets, "
                "open ports, identified vulnerabilities, severity ratings, and remediation suggestions. Reports are formatted for professional pentesting deliverables."
            ),

            "Automated Scheduling": (
                "Users can schedule regular scan runs using built-in cron integration. Configure intervals such as daily, weekly, or monthly scans "
                "to maintain continuous security monitoring with minimal manual intervention. Scheduled reports can be automatically generated and emailed."
            ),

            "Troubleshooting": (
                "If you experience issues, first verify that all dependencies such as Python and required tools are correctly installed. "
                "Check CyberSight’s log files for error details. Running the diagnostic command:\n\n"
                "  cybersight --diagnose\n\n"
                "will analyze your environment and output potential problems along with suggested fixes. For persistent issues, contact support."
            ),

            "Best Practices": (
                "To maximize effectiveness, run scans during periods of low network traffic to reduce false positives and avoid service disruptions. "
                "Review all findings carefully before reporting to minimize noise. Regularly update CyberSight and all integrated tools "
                "to ensure the latest vulnerability checks are included."
            ),

            "Contact Support": (
                "For assistance, you can email our support team at cybersightindia@gmail.com or join the CyberSight Discord community for real-time help from experts and other users. "
                "We encourage reporting bugs, feature requests, and sharing feedback to continuously improve CyberSight."
            ),
        }
        print(Fore.WHITE + help_responses.get(option, "Documentation coming soon. Please check official README for updates."))

def main():
    guide_shell = CyberSightGuideTerminal()
    guide_shell.run()

# Place the following in your project terminal entry point (replace 'vedantsh' with 'cybersight'):
if __name__ == "__main__":
    main()
