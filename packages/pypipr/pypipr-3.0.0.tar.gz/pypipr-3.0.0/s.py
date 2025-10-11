class PyPi:
    email = "ufiapjj@gmail.com"
    password = "dzukhron"

    class Token:
        name = "__token__"
        value = (
            "pypi-AgEIcHlwaS5vcmcCJGI0NzJhYTcwLWVmMjctNDQ0NS1hZjVjLTIyOT"
            "NiZWYyYzc3ZQACKlszLCJkMTdmMWM4OC0xZGVlLTQ5OWQtOWRjNy1mNjhhY"
            "jFkMjlhMDgiXQAABiAHa_VLiA5jhV-9mGcCIPANaWCSgFmZCcc53YK_XWcv3Q"
        )


import subprocess

subprocess.run(f"uv publish --token '{PyPi.Token.value}'", shell=True)
