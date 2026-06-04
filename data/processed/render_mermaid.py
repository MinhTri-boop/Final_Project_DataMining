import os
import re
import subprocess

FILES = [
    "backend_architecture.md",
    "frontend_architecture.md",
    "System_Architecture_Diagram.md"
]

def extract_mermaid(markdown_content):
    matches = re.findall(r'```mermaid\n(.*?)\n```', markdown_content, re.DOTALL)
    return matches

def main():
    base_dir = r"f:/Data_Mining_Final/data/processed"
    
    for file_name in FILES:
        file_path = os.path.join(base_dir, file_name)
        if not os.path.exists(file_path):
            print(f"Not found: {file_path}")
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        mermaids = extract_mermaid(content)
        
        for idx, mmd_content in enumerate(mermaids):
            base_name = file_name.replace(".md", "")
            suffix = f"_{idx+1}" if len(mermaids) > 1 else ""
            
            mmd_file = os.path.join(base_dir, f"{base_name}{suffix}.mmd")
            png_file = os.path.join(base_dir, f"{base_name}{suffix}.png")
            
            with open(mmd_file, "w", encoding="utf-8") as f:
                f.write(mmd_content)
                
            print(f"Generating {png_file} ...")
            try:
                # Use mmdc directly if installed globally, or via npx
                subprocess.run(["npx", "-y", "@mermaid-js/mermaid-cli", "-i", mmd_file, "-o", png_file], check=True, shell=True)
                print(f"Successfully generated {png_file}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to generate {png_file}: {e}")

if __name__ == "__main__":
    main()
