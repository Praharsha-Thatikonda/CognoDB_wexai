import os
import sys
import subprocess
import shutil

def check_env_file():
    env_file = ".env"
    example_file = ".env.example"
    
    if not os.path.exists(env_file):
        print("[-] .env file not found!")
        if os.path.exists(example_file):
            print(f"[*] Copying {example_file} to {env_file}...")
            shutil.copy(example_file, env_file)
            print("[!] Please open the .env file, fill in your database credentials, and then run this script again.")
            sys.exit(1)
        else:
            print("[-] .env.example also not found. Cannot proceed.")
            sys.exit(1)
            
    # Check if .env contains placeholder values
    with open(env_file, 'r') as f:
        content = f.read()
        if "<instance-id>" in content or "PASSWORD=\n" in content or "PASSWORD=\r\n" in content:
            print("[!] WARNING: Your .env file appears to contain placeholder values or empty passwords.")
            print("[!] The benchmark will likely fail if it attempts to connect to these databases.")
            response = input("Do you want to proceed anyway? (y/N): ")
            if response.lower() != 'y':
                print("Exiting...")
                sys.exit(0)
    print("[+] .env file check passed.")

def run_step(step_name, command):
    print(f"\n{'='*50}")
    print(f"[*] Starting Step: {step_name}")
    print(f"{'='*50}")
    
    try:
        # Use shell=True for pip on windows, else standard array
        process = subprocess.run(command, shell=True, check=True)
        print(f"[+] Successfully completed: {step_name}")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error executing {step_name}. Process exited with code {e.returncode}.")
        sys.exit(1)

def main():
    print("Welcome to the CognoDB Benchmark Runner")
    print("---------------------------------------")
    
    # 1. Check environment variables
    check_env_file()
    
    # 2. Run the pipeline (Equivalent to `make all`)
    
    # Setup
    run_step("Installing Requirements", "pip install -r requirements.txt")
    
    # Download / Prepare Data
    run_step("Preparing Dataset", f"{sys.executable} -m src.data.download_dataset")
    
    # Load Data
    run_step("Loading Data into Databases", f"{sys.executable} -m src.harness.loader")
    
    # Benchmark
    run_step("Running Benchmark Workloads", f"{sys.executable} -m src.harness.runner")
    
    # Report
    run_step("Generating Reports", f"{sys.executable} -m src.report.generate_report")
    
    print("\n[+] Benchmark Suite completed successfully!")
    print("[+] Check the README.md and report/charts/ directory for results.")

if __name__ == "__main__":
    main()
