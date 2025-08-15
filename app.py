# ... Flask imports ...
@app.route('/generate', methods=['POST'])
def generate():
    import io, datetime
    data = request.form.to_dict()
    # ...copy everything inside this function...
    # (See full function body below ↓)
    def generate_strategy_csv(data):
        ...   # (all loop logic: see below)
        return fileName, csv_content
    fileName, csv = generate_strategy_csv(data)
    return send_file(
        io.BytesIO(csv.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=fileName
    )
