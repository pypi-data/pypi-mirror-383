# multi_system_connector/cli.py

import uvicorn

def run():
    uvicorn.run("multi_system_connector.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
