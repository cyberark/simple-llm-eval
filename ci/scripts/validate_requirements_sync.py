#!/usr/bin/env python3
import sys
import subprocess

def main():

    try:
        export_cmd = ["uv", "export", "--format", "requirements-txt"]
        with open("ci/requirements-temp.txt", "w") as temp_file:
            result = subprocess.run(export_cmd, stdout=temp_file, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to export requirements: {result.stderr}")

        # Compare files
        cmp_cmd = ["cmp", "-s", "requirements.txt", "ci/requirements-temp.txt"]
        cmp_result = subprocess.run(cmp_cmd)
        if cmp_result.returncode != 0:
            # Files differ
            diff_cmd = ["diff", "-u", "requirements.txt", "ci/requirements-temp.txt"]
            subprocess.run(diff_cmd)
            error = "requirements.txt is out of date. Run 'uv export --format requirements-txt > requirements.txt' and commit the changes."
            raise RuntimeError(error)
        else:
            print("✅ requirements.txt is up to date.")
            sys.exit(0)

    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
