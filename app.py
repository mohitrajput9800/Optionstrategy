from flask import Flask, render_template, request, send_file
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Collect all form data
    ratio = request.form.get('ratio')
    script = request.form.get('script')
    legs = int(request.form.get('legs'))
    expiry = request.form.get('expiry')
    firstStrikeCE = request.form.get('firstStrikeCE')
    firstStrikePE = request.form.get('firstStrikePE')
    strikeStep = request.form.get('strikeStep')
    legGap = request.form.get('legGap')
    totStrikes = request.form.get('totStrikes')
    buySellPattern = request.form.get('buySellPattern').upper()
    fileName = request.form.get('fileName') or f"{script}-strategy.csv"
    lotSize = request.form.get('lotSize')

    # --- YOUR Protected CSV generator logic here ---
    # (This is a placeholder - replace with your real logic!)
    csv_lines = [
        "legs,ratio,script,expiry,firstStrikeCE,firstStrikePE,strikeStep,legGap,totStrikes,buySellPattern,fileName,lotSize",
        f"{legs},{ratio},{script},{expiry},{firstStrikeCE},{firstStrikePE},{strikeStep},{legGap},{totStrikes},{buySellPattern},{fileName},{lotSize}"
        # Add logic to generate all required rows (see your JS for the real logic)
    ]
    # -----------------------------------------------

    output = io.StringIO()
    output.write('\n'.join(csv_lines))
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=fileName
    )

if __name__ == "__main__":
    app.run()