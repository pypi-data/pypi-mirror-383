import sys
import platform
import pkg_resources
import os
import datetime

def pyinfo():
    libs = sorted([f"{d.project_name} {d.version}" for d in pkg_resources.working_set])
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Python Info</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #111;
                color: #ddd;
                padding: 20px;
            }}
            h1 {{
                color: #0b5;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }}
            td, th {{
                border: 1px solid #333;
                padding: 8px;
            }}
            a {{
                color: #0b5;
            }}
        </style>
    </head>
    <body>
        <h1>Python Info</h1>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Python version</td><td>{platform.python_version()}</td></tr>
            <tr><td>Implementation</td><td>{platform.python_implementation()}</td></tr>
            <tr><td>Build</td><td>{platform.python_build()}</td></tr>
            <tr><td>Compiler</td><td>{platform.python_compiler()}</td></tr>
            <tr><td>Platform</td><td>{platform.platform()}</td></tr>
            <tr><td>Architecture</td><td>{platform.architecture()[0]}</td></tr>
            <tr><td>System</td><td>{platform.system()} {platform.release()}</td></tr>
            <tr><td>Machine</td><td>{platform.machine()}</td></tr>
            <tr><td>Processor</td><td>{platform.processor()}</td></tr>
            <tr><td>Current Time</td><td>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td></tr>
        </table>
        <h2>Installed Packages</h2>
        <ul>
            {''.join(f'<li>{lib}</li>' for lib in libs)}
        </ul>
    </body>
    </html>
    """
    return html
