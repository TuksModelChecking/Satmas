import subprocess
import time

class OpenWBOSolver:
    def __init__(self, binary_path):
        self.binary_path = binary_path
        self.solver_name = "open-wbo"

    def solve(self, wcnf_file_path):
        print(f"[{self.solver_name}] Starting solver ({self.binary_path})...")
        results = {}
        try:
            start_time = time.time()
            process = subprocess.run(
                [self.binary_path, wcnf_file_path],
                capture_output=True,
                text=True,
                check=False
            )
            end_time = time.time()

            solution_model_str = None
            solution_model = None
            cost_str = None
            status = 'unknown'

            # Parse model and cost from stdout
            for line in process.stdout.splitlines():
                if line.startswith("v "):
                    solution_model_str = line[2:]
                    # convert to list of integers
                    solution_model = [int(x) for x in solution_model_str.split() if x.isdigit() or (x.startswith('-') and x[1:].isdigit())]
                if line.startswith("o "):
                    cost_str = line[2:]
                    try:
                        cost_str = int(cost_str) # Attempt to convert cost to int
                    except ValueError:
                        pass # Keep as string if not an int

            # Determine status based on stdout content first, then return code
            if "s OPTIMUM FOUND" in process.stdout or "s SATISFIABLE" in process.stdout:
                status = 'success'
            elif "s UNSATISFIABLE" in process.stdout:
                status = 'no solution (UNSAT)'
            
            results = {
                'stdout': process.stdout,
                'stderr': process.stderr,
                'return_code': process.returncode,
                'total_time': end_time - start_time,
                'status': status,
                'model': solution_model,
                'cost': cost_str
            }
            print(f"[{self.solver_name}] Finished with status: {status}.")
        except FileNotFoundError:
            message = f"Error: {self.solver_name} binary not found at {self.binary_path}"
            print(f"[{self.solver_name}] {message}")
            results = {'status': 'error', 'message': message}
        except Exception as e:
            message = f"Error during {self.solver_name} solving: {e}"
            print(f"[{self.solver_name}] {message}")
            results = {'status': 'error', 'message': str(e)}
        return results