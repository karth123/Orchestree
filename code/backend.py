from singletons import GoogleGeminiClientSingleton, OpenAIClientSingleton, LlamaClientSingleton
import re
from xml.sax.saxutils import escape, unescape

import requests
import os,glob
from diagrams import Diagram, Edge, Cluster
from diagrams.custom import Custom
import json,yaml
from subprocess import run, PIPE
from lxml import etree

class LLMInference:
    def __init__(self,api_key):
        self.gemini_google_client = GoogleGeminiClientSingleton.initialise_gemini_client()
        self.gemini_google_client_byok = GoogleGeminiClientSingleton.initialise_gemini_client_byok(api_key = api_key)
        self.openai_client = OpenAIClientSingleton.get_gpt4o_openai_client()
        self.llama_client = LlamaClientSingleton.get_llama_openai_client()

    def run_inference_google(self,input_data:str, system_prompt:str):
        ''' Use gemini 1.5 flash to run a chat completion. Working smoothly for both YAML creation and YAML icon match with 90% accuracy'''
        prompt = system_prompt + input_data
        response = self.gemini_google_client.generate_content(prompt)
        def remove_code_block_markers(text):
            # Remove the starting ```python
            text = re.sub(r'^```yaml', '', text, flags=re.MULTILINE)
            # Remove the ending ```
            text = re.sub(r'```$', '', text, flags=re.MULTILINE)
            # Strip leading and trailing whitespace
            return text.strip()
        cleaned_response = remove_code_block_markers(response.text)
        return cleaned_response
    
    def run_inference_google_byok(self,input_data:str, system_prompt:str):
        ''' Use gemini 1.5 flash to run a chat completion. Working smoothly for both YAML creation and YAML icon match with 90% accuracy'''
        prompt = system_prompt + input_data
        response = self.gemini_google_client_byok.generate_content(prompt)
        def remove_code_block_markers(text):
            # Remove the starting ```python
            text = re.sub(r'^```yaml', '', text, flags=re.MULTILINE)
            # Remove the ending ```
            text = re.sub(r'```$', '', text, flags=re.MULTILINE)
            # Strip leading and trailing whitespace
            return text.strip()
        cleaned_response = remove_code_block_markers(response.text)
        return cleaned_response
    def run_inference_llama(self, input_data:str, system_prompt:str):
        ''' Use Llama in huggingface for chat completion. Not working and not in development'''
        prompt = system_prompt + input_data
        messages = [
            {
                "role": "user",
                "content" : prompt
            }
        ]
        response = self.llama_client.chat.completions.create(
            model = "meta-llama/Llama-3.2-11B-Vision-Instruct",
            messages = messages,
        )
        output = response.choices[0].message.content
        def remove_code_block_markers(text):
            # Remove the starting ```python
            text = re.sub(r'^```yaml', '', text, flags=re.MULTILINE)
            # Remove the ending ```
            text = re.sub(r'```$', '', text, flags=re.MULTILINE)
            # Strip leading and trailing whitespace
            return text.strip()
        cleaned_response = remove_code_block_markers(output)
        return cleaned_response
    
class YAMLTransformer:

    @staticmethod
    def generate_yaml_from_prompt(input_data:str,system_prompt:str):
        api_key = "NULL"                                          # Generates YAML configuration from user provided input data. User answers 3 questions and provides a list of icons as multiselect
        return LLMInference(api_key = api_key).run_inference_google(input_data = input_data, system_prompt = system_prompt)
    @staticmethod
    def transform_yaml_with_icons(input_yaml:str, cloud_icons:str, system_prompt:str):
        api_key = "NULL"   # Using user provided icon set (Through multiselect), gemini transforms yaml to replace placeholder paths with icon-references
        input_data = input_yaml + cloud_icons
        return LLMInference(api_key = api_key).run_inference_google(input_data = input_data, system_prompt = system_prompt)
    
    @staticmethod
    def generate_yaml_from_prompt_byok(input_data:str,system_prompt:str, api_key:str):                                          # Generates YAML configuration from user provided input data. User answers 3 questions and provides a list of icons as multiselect
        return LLMInference(api_key = api_key).run_inference_google_byok(input_data = input_data, system_prompt = system_prompt)
    @staticmethod
    def transform_yaml_with_icons_byok(input_yaml:str, cloud_icons:str, system_prompt:str,api_key:str):   # Using user provided icon set (Through multiselect), gemini transforms yaml to replace placeholder paths with icon-references
        input_data = input_yaml + cloud_icons
        return LLMInference(api_key = api_key).run_inference_google_byok(input_data = input_data, system_prompt = system_prompt)
    @staticmethod
    def transform_yaml_with_icon_paths(yaml_string:str,icon_descriptor_path, exception_icon_path):   # Icon references are mapped to true icon paths (Icons are locally stored)
        """
        Processes a YAML string by modifying its resources' icons based on direct regex matching.
        If a resource's current icon value matches one of the regex patterns from the icon descriptor,
        replace it with the corresponding icon path. If no regex matches, use the exception icon.
        """

        if not os.path.exists(icon_descriptor_path):
            raise FileNotFoundError(f"Icon descriptor file '{icon_descriptor_path}' not found.")

        try:
            # Parse the YAML string
            data = yaml.safe_load(yaml_string)

            with open(icon_descriptor_path, 'r') as file:
                icon_descriptor = json.load(file)

            # Process resources if they exist
            if data and 'diagram' in data and 'resources' in data['diagram']:
                YAMLTransformer.process_resources(data['diagram']['resources'], icon_descriptor, exception_icon_path)
            else:
                print("No 'diagram.resources' section found in YAML.")

            return yaml.dump(data, sort_keys=False)

        except yaml.error.YAMLError as e:
            raise RuntimeError(f"ScannerError while processing YAML: {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")
    @staticmethod    
    def process_resources(resources, icon_descriptor, exception_icon_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        """
        Recursively process resources, updating their icons based on regex matches from the icon descriptor.
        """
        for resource in resources:
            if 'icon' in resource:
                current_icon = str(resource['icon'])
                matched_icon = None

                # Attempt regex matches against the icon descriptor keys
                for pattern, icon_path in icon_descriptor.items():
                    normalized_icon_path = re.sub(r"\\", "/", icon_path)
                    if re.search(pattern, current_icon):
                        matched_icon = os.path.abspath(os.path.join(base_dir, normalized_icon_path))
                        break

                # If no match found, use exception icon
                if not matched_icon:
                    matched_icon = exception_icon_path

                resource['icon'] = matched_icon

            # If this resource has nested resources, process them too
            if 'of' in resource and isinstance(resource['of'], list):
                YAMLTransformer.process_resources(resource['of'], icon_descriptor, exception_icon_path)


# Global dictionaries to store resources and relationships
resources = {}
relationships = []

def separate_relates(resources_list, relates_list):   # Helper function to generate the graphviz dot file.
    cleaned_resources = []
    for item in resources_list:
        if 'relates' in item:
            relates_list.append(item['relates'])
        else:
            if 'of' in item:
                item['of'] = separate_relates(item['of'], relates_list)
            cleaned_resources.append(item)
    return cleaned_resources

def process_resource(resource, parent_id, group=None):  # Helper function to generate graphviz dot file from YAML
    resource_id = resource['id']
    resource_type = resource['type']
    label = resource['name']
    resource_of = resource.get('of', [])

    if resource_type == 'cluster':
        # Create a Cluster context
        with Cluster(label):
            for sub_resource in resource_of:
                process_resource(sub_resource, resource_id)
    elif resource_type == 'group':
        # Create a group (collect nodes into a list)
        group_nodes = []
        for sub_resource in resource_of:
            process_resource(sub_resource, resource_id, group_nodes)
        resources[resource_id] = group_nodes
        if group is not None:
            group.extend(group_nodes)
    elif resource_type == 'custom':
        # Create the custom node
        icon_path = resource.get('icon')
        if not icon_path:
            raise ValueError(f"Custom node '{label}' must have an 'icon' path specified.")
        node_instance = Custom(label=label, icon_path=icon_path)
        resources[resource_id] = node_instance
        if group is not None:
            group.append(node_instance)
    else:
        raise ValueError(f"Unsupported resource type '{resource_type}' for resource '{label}'")

def connect_nodes(from_node, edge, to_node, direction): # Helper function to generate graphviz dot file from YAML
    if direction == 'outgoing':
        from_node >> edge >> to_node
    elif direction == 'incoming':
        from_node << edge << to_node
    elif direction == 'bidirectional':
        from_node << edge >> to_node
    else:
        from_node - edge - to_node

def generate_svg_from_yaml(yaml_content):   # Performs two tasks: Generates a dot file from the YAML, and uses graphviz internal SVG renderer to convert dot to SVG. The SVG generated from this references to icon svgs using local paths as xlink:href
    # Parse YAML content
    yaml_data = yaml.safe_load(yaml_content)

    diagram_config = yaml_data['diagram']
    diagram_name = diagram_config.get('name', '')
    diagram_direction = diagram_config.get('direction', 'left-to-right')
    diagram_style = diagram_config.get('style', {})
    resources_list = diagram_config.get('resources', [])
    if 'relates' not in yaml_data.get('diagram', {}):
        relates_list = yaml_data.get('relates', [])
    else:
        relates_list = yaml_data['diagram']['relates']

    # Separate 'relates' entries from 'resources' recursively
    resources_list = separate_relates(resources_list, relates_list)

    direction_map = {
        'left-to-right': 'LR',
        'right-to-left': 'RL',
        'top-to-bottom': 'TB',
        'bottom-to-top': 'BT'
    }
    diagram_direction = direction_map.get(diagram_direction, 'LR')

    with Diagram(
        name=diagram_name,
        direction=diagram_direction,
        outformat='dot',
        show=False,
        graph_attr=diagram_style.get('graph', {}),
        node_attr=diagram_style.get('node', {}),
        edge_attr=diagram_style.get('edge', {}),
    ) as diagram:
        global resources, relationships
        resources = {}
        relationships = []

        for resource in resources_list:
            process_resource(resource, 'diagram')

        for relation in relates_list:
            from_resource_id = relation['from']
            to_resource_id = relation['to']
            from_node = resources.get(from_resource_id)
            to_node = resources.get(to_resource_id)
            if from_node is None or to_node is None:
                continue

            edge = Edge(
                label=relation.get('description', ''),
                color=relation.get('color', ''),
                style=relation.get('style', '')
            )
            direction = relation.get('direction', 'outgoing')

            if isinstance(from_node, list) and isinstance(to_node, list):
                for fn in from_node:
                    for tn in to_node:
                        connect_nodes(fn, edge, tn, direction)
            elif isinstance(from_node, list):
                for fn in from_node:
                    connect_nodes(fn, edge, to_node, direction)
            elif isinstance(to_node, list):
                for tn in to_node:
                    connect_nodes(from_node, edge, tn, direction)
            else:
                connect_nodes(from_node, edge, to_node, direction)

        dot_output = diagram.dot.source

    try:
        result = run([ "dot", "-Tsvg"], input=dot_output, text=True, stdout=PIPE, stderr=PIPE, check=True)
        print(result.stdout)
        return result.stdout
    except Exception as e:
        raise RuntimeError(f"Error generating SVG: {e}")

def remove_all_dot_files():
    try:
        # Get all .dot files in the current working directory
        dot_files = glob.glob("*.dot")
        
        if not dot_files:
            print("No .dot files found in the current directory.")
            return

        # Iterate over all .dot files and delete them
        deleted_files = []
        for dot_file in dot_files:
            os.remove(dot_file)
            deleted_files.append(dot_file)
        
        # Print the list of deleted files
        print(f"Deleted the following .dot files:")
        for file in deleted_files:
            print(f"- {file}")
    except Exception as e:
        print(f"Error while deleting .dot files: {e}")

class SVGTransformer:
    @staticmethod    
    def parse_dimension(value):   # Helper function to generate the pure svg code
        """
        Parse a dimension value from an SVG attribute, removing units (e.g. 'px').
        Returns a float or raises ValueError if it cannot parse.
        """
        if value is None:
            raise ValueError("No dimension value provided")
        # Remove any trailing units (px, pt, etc.)
        # This is a simple approach. More sophisticated unit handling can be implemented if needed.
        return float(value.replace('px', '').strip())
    
    @staticmethod
    def get_original_dimensions(icon_root):  # Helper function to get the pure svg code
        """
        Determine the original width and height of the referenced SVG icon.
        Priority:
        1. viewBox
        2. width/height attributes on svg element
        Raises ValueError if unable to determine dimensions.
        """
        # Attempt to get from viewBox first
        viewBox = icon_root.get('viewBox')
        if viewBox:
            vb_parts = viewBox.split()
            if len(vb_parts) == 4:
                # Typically viewBox = "minX minY width height"
                _, _, vb_w, vb_h = vb_parts
                return float(vb_w), float(vb_h)

        # If no viewBox, try width/height attributes
        w = icon_root.get('width')
        h = icon_root.get('height')

        if w and h:
            return SVGTransformer.parse_dimension(w), SVGTransformer.parse_dimension(h)

        # If we reach here, we cannot determine original dimensions
        raise ValueError("Unable to determine original dimensions of the SVG icon.")
    @staticmethod
    def get_svg_code(main_svg_code):  # The local svg code with xlink:href references is accessed by this function and the icon code is accessed. The icon svg code is transformed into the main svg chassis. The output svg has no references to local paths and uses pure svg code for the icons.
        def sanitize_svg(svg_code):
            svg_code = svg_code.replace('&', '&amp;')
        # Parse the SVG as a string
            parser = etree.XMLParser(remove_comments=False, recover=True)
            root = etree.fromstring(svg_code.encode('utf-8'), parser)

            # Iterate through all elements and escape attributes and text content
            for element in root.iter():
                # Escape all attribute values
                for attr, value in element.attrib.items():
                    if value:
                        # Special handling for xlink:href to preserve & correctly
                        if attr == '{http://www.w3.org/1999/xlink}href':
                            # Ensure & is replaced properly in href
                            value = value.replace('&', '&amp;')
                        else:
                            value = escape(value)
                        element.set(attr, value)
                
                # Escape text content
                if element.text:
                    element.text = escape(element.text)

                # Escape tail content (text after closing tag)
                if element.tail:
                    element.tail = escape(element.tail)
            
            # Serialize back to string
            sanitized_svg = etree.tostring(root, xml_declaration=True, encoding='UTF-8').decode('utf-8')
            return sanitized_svg
        main_svg_code = sanitize_svg(main_svg_code)
        parser = etree.XMLParser(remove_comments=False)
        # Parse the SVG as bytes (to handle XML declarations)
        root = etree.fromstring(main_svg_code.encode('utf-8'), parser)

        # Define a namespace map
        # svg namespace for the main SVG elements
        # xlink namespace for the xlink attributes
        nsmap = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        # Now we can query using these namespaces
        # Notice the "svg:image" instead of just "image"
        images = root.xpath('.//svg:image[@xlink:href]', namespaces=nsmap)

        for img in images:
            href = img.get('{http://www.w3.org/1999/xlink}href')
            if not unescape(href) or not os.path.exists(unescape(href)):
                print(href)
                print(unescape(href))
                print(f"Warning: Missing href in image element. Skipping...")
                continue
            # Extract transform parameters from the image
            width_attr = img.get('width')
            height_attr = img.get('height')
            x_attr = img.get('x')
            y_attr = img.get('y')

            # Parse numeric values, default to 0 for x/y if missing
            width = SVGTransformer.parse_dimension(width_attr) if width_attr else 0.0
            height = SVGTransformer.parse_dimension(height_attr) if height_attr else 0.0
            x = float(x_attr) if x_attr else 0.0
            y = float(y_attr) if y_attr else 0.0

            # Parse the referenced SVG
            icon_tree = etree.parse(unescape(href), parser)
            icon_root = icon_tree.getroot()

            # Get original dimensions of the referenced icon
            try:
                original_w, original_h = SVGTransformer.get_original_dimensions(icon_root)
            except ValueError:
                # Handle the case where we cannot determine dimensions
                # For safety, continue or raise
                continue

            # Compute scale
            scaleX = width / original_w if original_w != 0 else 1
            scaleY = height / original_h if original_h != 0 else 1

            # Create a new <g> element to contain the inline SVG
            g = etree.Element('g')
            g.set('transform', f'translate({x},{y}) scale({scaleX},{scaleY})')

            # Move all children of icon_root (except svg itself) into <g>
            # We'll append the children directly; this removes them from icon_root in icon_tree
            # If you need to preserve the original, clone them.
            for child in list(icon_root):
                icon_root.remove(child)
                g.append(child)

            # Replace the image element with the new <g>
            parent = img.getparent()
            parent.replace(img, g)
        result_bytes = etree.tostring(root, xml_declaration=True, encoding='UTF-8')
        result_str = result_bytes.decode('UTF-8')
        # Convert back to string
        return result_str



