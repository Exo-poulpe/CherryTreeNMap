import jinja2
import time
import sys
from enum import Enum
import argparse


class Color(Enum):
    GREEN = '#33d17a'
    RED = '#e01b24'
    BLUE = '#3584e4'

def parse_gnmap(gnmap_file):
    nodes = []
    with open(gnmap_file, 'r') as file:
        for line in file:
            if "Up" in line:
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
                    "data": data,
                })
    return nodes

def generate_cherrytree_ctd(nodes, template_file, output_file):
    # Load Jinja2 template
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)

    # Render the template with data
    outputText = template.render(nodes=nodes)

    # Write the output to a file
    with open(output_file, 'w') as file:
        file.write(outputText)


def main(args):
    # Example usage
    gnmap_file =  args.file
    template_file = args.template
    output_ctd_file = args.output

    nodes = parse_gnmap(gnmap_file)
    generate_cherrytree_ctd(nodes, template_file, output_ctd_file)

    print("CherryTree CTD file has been generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')

    # Add the arguments
    parser.add_argument('--file','-f', type=str, help='the .GNMAP file to process')
    parser.add_argument('--template','-t', type=str, help='the template Jinj2 to use')
    parser.add_argument('--output','-o' ,type=str, help='the output file .CTD to have')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase output verbosity (option can be stacked, e.g., -vv is more verbose than -v)')

    # Execute the parse_args() method
    args = parser.parse_args()
    main(args)

