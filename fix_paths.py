import sys
with open('tpua_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from i18n_helper import _', 'from i18n_helper import _, get_resource_path')

old_logo = 'logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))'
new_logo = '''logo_path = str(get_resource_path(os.path.join("assets", "TPUA.png")))
        if not os.path.exists(logo_path):
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))'''
content = content.replace(old_logo, new_logo)

old_tpua = 'tpua_logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))'
new_tpua = '''tpua_logo_path = str(get_resource_path(os.path.join("assets", "TPUA.png")))
        if not os.path.exists(tpua_logo_path):
            tpua_logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))'''
content = content.replace(old_tpua, new_tpua)

with open('tpua_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
