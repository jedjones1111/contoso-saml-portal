import os
import base64
import zlib
from flask import Flask, request, redirect, session, render_template, send_from_directory, url_for
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'contoso-demo-secret-change-in-prod')

# ── SAML HELPER ──
def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=os.path.join(os.path.dirname(__file__), 'saml'))
    return auth

def prepare_flask_request(request):
    url_data = request.url.split('?')
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': request.environ.get('SERVER_PORT', '443'),
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
    }

# ── ROUTES ──
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('portal.html', user=session['user'], email=session['email'])

@app.route('/login')
def login():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    return redirect(auth.login())

@app.route('/saml/acs', methods=['POST'])
def saml_acs():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    auth.process_response()
    errors = auth.get_errors()

    if errors:
        return f"SAML Error: {', '.join(errors)} - {auth.get_last_error_reason()}", 400

    if not auth.is_authenticated():
        return "Authentication failed", 401

    attributes = auth.get_attributes()
    name_id = auth.get_nameid()

    # Extract user info from SAML attributes
    display_name = name_id
    email = name_id

    for attr_name, attr_values in attributes.items():
        if attr_values:
            lower = attr_name.lower()
            if 'displayname' in lower or 'name' in lower:
                display_name = attr_values[0]
            if 'emailaddress' in lower or 'mail' in lower or 'upn' in lower:
                email = attr_values[0]

    session['user'] = display_name
    session['email'] = email
    session['saml_nameid'] = name_id

    return redirect(url_for('index'))

@app.route('/saml/metadata')
def saml_metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if errors:
        return f"Metadata errors: {', '.join(errors)}", 500

    return metadata, 200, {'Content-Type': 'text/xml'}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── STATIC FILE DOWNLOADS ──
# These routes serve the actual document files
# MDCA session policy intercepts the HTTP response and applies the sensitivity label
@app.route('/files/<filename>')
def download_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    files_dir = os.path.join(os.path.dirname(__file__), 'static', 'files')
    return send_from_directory(files_dir, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
