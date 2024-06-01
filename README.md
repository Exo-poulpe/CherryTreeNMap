
## Description
This program processes GNMAP files to generate a CherryTree display of identified IP addresses. It automates the capture of screenshots for ports 80 and 443 using HTTPx, enhancing network analysis and reporting. Furthermore, for ports 21, 22, and 5901, the program compiles a list of IP addresses with active services on these ports. It also generates scripts to use Hydra for brute-forcing services found on these ports, streamlining the security testing process.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Exo-poulpe/CherryTreeNMap
   cd CherryTreeNMap
   ```

2. **Install required packages:**
   Ensure you have Python and pip installed on your system, then run:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

```bash
python internal_weapons_attack.py [options]
```

### Options

- `--file, -f`: Specify the .GNMAP file to process.
- `--template, -t`: Specify the Jinja2 template file to use.
- `--output, -o`: Define the output file (.CTD).
- `--remove, -rm`: Remove username wordlist, password wordlist, and HTTPx binary after processing.
- `--httpx-dir`: Specify the output folder for HTTPx screenshots. Default is `httpx_output`.
- `--verbose, -v`: Increase output verbosity. Use multiple `v`s for higher verbosity (e.g., `-vvv`).

### Examples

**Basic Usage:**
```bash
python internal_weapons_attack.py -f scan_result.gnmap -t cherry.j2 -o output.ctd
```

**Remove Temporary Files:**
```bash
python internal_weapons_attack.py  -rm
```

## NMAP scan

To perform a comprehensive network scan, the recommended option is:

```bash
sudo nmap -sT -sV -p- --open --reason -v -oA scan_result 127.0.0.1/8
```

### Explanation of Options:
- `-sT`: TCP connect scan, utilizes TCP protocol to establish a connection.
- `-sV`: Probes open ports to determine service/version information.
- `-p-`: Scans all 65535 ports.
- `--open`: Shows only open (or possibly open) ports.
- `--reason`: Displays the reason a port is set to a specific state.
- `-v`: Increases verbosity level.
- `-oA scan_result`: Outputs in all formats (`nmap`, `gnmap`, `xml`) with the base filename `scan_result`.

For a faster scan, consider:

```bash
sudo nmap -sT -sV --top-ports=1024 -n --open --reason -v -oA scan_result 127.0.0.1/8
```

### Additional Speed-Optimized Options:
- `--top-ports=1024`: Scans the top 1024 most common ports.
- `-n`: Skips DNS resolution to speed up the scan.

For even greater speed, you can use Masscan to scan specified ports:

```bash
sudo masscan 127.0.0.1/8 -p22,21,80,443,445 -oG masscan_grep_output.txt
```

### Masscan Options Explained:
- `-p22,21,80,443,445`: Specifies the ports 22 (SSH), 21 (FTP), 80 (HTTP), 443 (HTTPS), and 445 (SMB) for scanning.
- `-oG`: Outputs in grepable format to the specified file.

Further refine your scans based on Masscan results:

```bash
sudo nmap -sT -sV -T4 --top-ports=1024 -n --open --reason -v -oA scan_result -iL input_filename.txt
```

### Nmap Post-Masscan Options:
- `-T4`: Sets the timing template to "aggressive," speeding up the scan.
- `-iL input_filename.txt`: Uses a list of IP addresses generated from the Masscan output as the input.

