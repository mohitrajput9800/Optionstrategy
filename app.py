from flask import Flask, render_template, request, send_file
import io

app = Flask(__name__)

@app.route('/')
def index():
    # This requires "form.html" in your templates folder
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Collect form data
    legs = int(request.form.get('legs', 3))
    ratio = request.form.get('ratio', '1.5.4')
    script = request.form.get('script', 'NIFTY').upper()
    expiry_raw = request.form.get('expiry', '')
    firstStrikeCE = int(request.form.get('firstStrikeCE', 24100))
    firstStrikePE = int(request.form.get('firstStrikePE', 25400))
    strikeStep = int(request.form.get('strikeStep', 50))
    legGap_input = request.form.get('legGap', '250')
    totStrikes = int(request.form.get('totStrikes', 10))
    buySellPattern = request.form.get('buySellPattern', 'S.B.S').upper()
    fileName = request.form.get('fileName') or f"{script}-strategy.csv"
    lotSize = request.form.get('lotSize', '75')
    mode = request.form.get('mode', '8184')  # '8184', '7155', or 'IOC'

    # Helper functions
    def formatExpiry(dateStr):
        from datetime import datetime
        if not dateStr:
            return ""
        try:
            d = datetime.strptime(dateStr, '%Y-%m-%d')
        except Exception:
            return ""
        months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        return f"{d.day:02d}-{months[d.month-1]}-{d.year}"

    def getStgCode(ratioStr):
        count = len(ratioStr.split('.'))
        if mode == "IOC":
            return 210
        if count == 2:
            return 10201
        if count == 3:
            return 10301
        if count == 4:
            return 10401
        return 10301

    expiry = formatExpiry(expiry_raw)
    gapValues = [int(x.strip()) for x in legGap_input.split(',') if x.strip().isdigit() and int(x.strip()) > 0]
    if not gapValues:
        gapValues = [250]
    blockQtys = [25000, 20000]

    headerLine = "#PID,cost,bcmp,scmp,flp,stgcode,script,lotsize,itype,expiry,otype,stkprice,ratio,buysell,pnAdd,pnMulti,bsoq,bqty,bprice,sprice,sqty,ssoq,btrQty,strQty,gap,ticksize,orderDepth,priceDepth,thshqty,allowedBiddepth,allowedSlippage,tradeGear,shortflag,isBidding,marketOrderRetries,marketOrLimitOrder,isBestbid,unhedgedActionType,TERActionType,BidWaitingType,param2,param3,param4,param5,param6,param7,param01,param02,param03,param04,param05,param06,param07,param08,param09,param10,param11,param12,param13,param14,param15,param16,param17,param18,param19,param20,param21,param22,param23,param24,param25,param26,param27,param28,param29,param30,param31,param32,param33,param34,param35,param36,param37,param38,param39,param40,param301,param302,param303,param304,param305,param306,param307,param308,param309,param310,param311,param312,param313,param314,param315,param316,param317,param318,param319,param320,param321,param322,param323,param324,param325,param326,param327,param328,param329,param330,param331,param332,param333,param334,param335,param336,param337,param338,param339,param340"
    headers = headerLine.split(",")
    rows = [headerLine]
    pid = 1
    stgCode = getStgCode(ratio)
    legsArr = ratio.split('.')
    legCount = len(legsArr)
    baseParts = buySellPattern.split('.')
    baseCount = len(baseParts)
    try:
        lots = [int(x) for x in lotSize.split('|')] if '|' in lotSize else [int(lotSize)] * legCount
    except Exception:
        lots = [75] * legCount

    for gap in gapValues:
        for qty in blockQtys:
            # -- Calls CE
            otypeLegs = '|'.join(['CE'] * legCount)
            expStr = '|'.join([expiry] * legCount)
            buySellStr = '.'.join([baseParts[i % baseCount] for i in range(legCount)])
            for i in range(totStrikes):
                prices = [firstStrikeCE + i * strikeStep + j * gap for j in range(legCount)]
                row = ['0'] * len(headers)
                row[0] = str(pid)
                pid += 1
                row[5] = str(stgCode)
                row[6] = script
                row[7] = lotSize
                row[8] = '-'.join(['OPTIDX'] * legCount)
                row[9] = expStr
                row[10] = otypeLegs
                row[11] = '|'.join(map(str, prices))
                row[12] = ratio
                row[13] = buySellStr
                row[15] = '1'
                row[18] = '0'
                row[19] = '0'
                row[25] = '10'
                row[26] = '2'
                row[27] = '2'
                row[29] = '5'
                row[30] = '50' if mode == "IOC" else '200'
                row[31] = '2'
                row[32] = '1'
                row[33] = '0' if mode == "IOC" else '1'
                row[34] = '5'
                row[37] = '2'
                row[38] = '1'
                row[39] = '500'
                row[46] = '60'
                row[47] = '50' if mode == "IOC" else '800'
                row[50] = '100'
                row[51] = '200'
                row[52] = '2575'
                row[53] = '60'
                row[54] = '100'
                row[55] = '200'
                row[56] = '100'
                row[57] = '100'
                row[58] = '10'
                row[60] = '1'
                row[64] = '1999'
                row[66] = '30'
                row[68] = '10'
                row[86] = '101'
                row[28] = '80' if mode == "IOC" else '0'
                row[24] = str(gap)
                rows.append(','.join(row))
            # -- Calls PE
            otypeLegs = '|'.join(['PE'] * legCount)
            expStr = '|'.join([expiry] * legCount)
            buySellStr = '.'.join([baseParts[i % baseCount] for i in range(legCount)])
            for i in range(totStrikes):
                prices = [firstStrikePE - i * strikeStep - j * gap for j in range(legCount)]
                row = ['0'] * len(headers)
                row[0] = str(pid)
                pid += 1
                row[5] = str(stgCode)
                row[6] = script
                row[7] = lotSize
                row[8] = '-'.join(['OPTIDX'] * legCount)
                row[9] = expStr
                row[10] = otypeLegs
                row[11] = '|'.join(map(str, prices))
                row[12] = ratio
                row[13] = buySellStr
                row[15] = '1'
                row[18] = '0'
                row[19] = '0'
                row[25] = '10'
                row[26] = '2'
                row[27] = '2'
                row[29] = '5'
                row[30] = '50' if mode == "IOC" else '200'
                row[31] = '2'
                row[32] = '1'
                row[33] = '0' if mode == "IOC" else '1'
                row[34] = '5'
                row[37] = '2'
                row[38] = '1'
                row[39] = '500'
                row[46] = '60'
                row[47] = '50' if mode == "IOC" else '800'
                row[50] = '100'
                row[51] = '200'
                row[52] = '2575'
                row[53] = '60'
                row[54] = '100'
                row[55] = '200'
                row[56] = '100'
                row[57] = '100'
                row[58] = '10'
                row[60] = '1'
                row[64] = '1999'
                row[66] = '30'
                row[68] = '10'
                row[86] = '101'
                row[28] = '80' if mode == "IOC" else '0'
                row[24] = str(gap)
                rows.append(','.join(row))

    csv_content = '\n'.join(rows)
    output = io.StringIO()
    output.write(csv_content)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=fileName
    )

if __name__ == '__main__':
    app.run(debug=True)
