from flask import Flask, render_template, request, send_file
import io

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/generate", methods=["POST"])
def generate():
    # 1. Get parameters
    ratio = request.form.get("ratio", "1.5.4")
    script = request.form.get("script", "NIFTY").upper()
    expiry_raw = request.form.get("expiry", "")
    strikeStep = int(request.form.get("strikeStep", 50))
    legGap_input = request.form.get("legGap", "250")
    totStrikes = int(request.form.get("totStrikes", 10))
    buySellPattern = request.form.get("buySellPattern", "S.B.S").upper()
    fileName = request.form.get("fileName") or f"{script}-strategy.csv"
    mode = request.form.get("mode", "8184")

    ce_pe_starts = {
        "NIFTY": (24000, 25000),
        "BANKNIFTY": (50000, 55000),
        "SENSEX": (78000, 80000),
        "MIDCAP": (11000, 12000),
        "FINNIFTY": (25000, 26000)
    }
    firstStrikeCE, firstStrikePE = ce_pe_starts.get(script, (24000, 25000))

    lotUnit = 75
    if script == "BANKNIFTY": lotUnit = 35
    elif script == "SENSEX": lotUnit = 20
    elif script == "MIDCAP": lotUnit = 140
    elif script == "FINNIFTY": lotUnit = 65

    if mode == "7155":
        legsArr = [seg for seg in ratio.strip().split('.') if seg.strip()]
        legCount = len(legsArr)
        lotSize = "|".join([str(lotUnit)] * (legCount if legCount > 0 else 2))
    else:
        legsArr = [seg for seg in ratio.strip().split('.') if seg.strip()]
        legCount = len(legsArr) if legsArr else 2
        lotSize = str(lotUnit)

    def format_expiry(date_str):
        from datetime import datetime
        if not date_str:
            return ""
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return ""
        months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        return f"{d.day:02d}-{months[d.month-1]}-{d.year}"

    def get_stg_code():
        if mode == "IOC": return 210
        count = len([seg for seg in ratio.split(".") if seg.strip()])
        if count == 2: return 10201
        if count == 3: return 10301
        if count == 4: return 10401
        return 10301

    expiry = format_expiry(expiry_raw)
    try:
        gapValues = [int(x.strip()) for x in legGap_input.split(",") if x.strip().isdigit() and int(x.strip()) > 0]
    except:
        gapValues = [250]
    if not gapValues: gapValues = 
    blockQtys = [25000, 20000]
    stgCode = get_stg_code()
    baseParts = [b for b in buySellPattern.split(".") if b]
    baseCount = len(baseParts) if baseParts else 1

    # 2. Prepare CSV header
    headerLine = "#PID,cost,bcmp,scmp,flp,stgcode,script,lotsize,itype,expiry,otype,stkprice,ratio,buysell,pnAdd,pnMulti,bsoq,bqty,bprice,sprice,sqty,ssoq,btrQty,strQty,gap,ticksize,orderDepth,priceDepth,thshqty,allowedBiddepth,allowedSlippage,tradeGear,shortflag,isBidding,marketOrderRetries,marketOrLimitOrder,isBestbid,unhedgedActionType,TERActionType,BidWaitingType,param2,param3,param4,param5,param6,param7,param01,param02,param03,param04,param05,param06,param07,param08,param09,param10,param11,param12,param13,param14,param15,param16,param17,param18,param19,param20,param21,param22,param23,param24,param25,param26,param27,param28,param29,param30,param31,param32,param33,param34,param35,param36,param37,param38,param39,param40,param301,param302,param303,param304,param305,param306,param307,param308,param309,param310,param311,param312,param313,param314,param315,param316,param317,param318,param319,param320,param321,param322,param323,param324,param325,param326,param327,param328,param329,param330,param331,param332,param333,param334,param335,param336,param337,param338,param339,param340"
    headers = headerLine.split(",")
    lines = [headerLine]
    pid = 1

    # 3. Fill All Data Rows (CE & PE both for each gap/qty)
    for gap in gapValues:
        for qty in blockQtys:
            otypeLegs_CE = "|".join(["CE"] * legCount)
            otypeLegs_PE = "|".join(["PE"] * legCount)
            expStr = "|".join([expiry] * legCount)
            buySellStr = ".".join([baseParts[i % baseCount] for i in range(legCount)])

            # ---- CE Rows ----
            for i in range(totStrikes):
                row = ['0'] * len(headers)
                prices = [firstStrikeCE + i * strikeStep + j * gap for j in range(legCount)]
                row[0] = str(pid); pid += 1
                row[2] = str(stgCode); row[3] = script; row[4] = lotSize
                row[5] = '-'.join(['OPTIDX'] * legCount)
                row[6] = expStr; row[7] = otypeLegs_CE; row[8] = "|".join(map(str, prices))
                row[9] = ratio; row[10] = buySellStr; row[11] = "1"
                row[12] = "0"; row[13] = "0"; row = "10"; row = "2"; row = "2"; row = "5"
                row = "50" if mode == "IOC" else "200"   # param02
                row = "2"; row = "1"; row = "0" if mode == "IOC" else "1"
                row = "5"; row = "2"; row = "1"; row = "500"; row = "60"
                row = "50" if mode == "IOC" else "800"   # allowedSlippage
                row = "100"; row = "200"; row = "2575"; row = "60"; row = "100"
                row = "200"; row = "100"; row = "100"; row = "10"; row = "1"
                row = "1999"; row = "30"; row = "10"; row = "101"
                row = "80" if mode == "IOC" else "0"      # thshqty
                row = str(gap)
                lines.append(",".join(row))
            # ---- PE Rows ----
            for i in range(totStrikes):
                row = ['0'] * len(headers)
                prices = [firstStrikePE - i * strikeStep - j * gap for j in range(legCount)]
                row = str(pid); pid += 1
                row[2] = str(stgCode); row[3] = script; row[4] = lotSize
                row[5] = '-'.join(['OPTIDX'] * legCount)
                row[6] = expStr; row[7] = otypeLegs_PE; row[8] = "|".join(map(str, prices))
                row[9] = ratio; row[10] = buySellStr; row[11] = "1"
                row[12] = "0"; row[13] = "0"; row = "10"; row = "2"; row = "2"; row = "5"
                row = "50" if mode == "IOC" else "200"   # param02
                row = "2"; row = "1"; row = "0" if mode == "IOC" else "1"
                row = "5"; row = "2"; row = "1"; row = "500"; row = "60"
                row = "50" if mode == "IOC" else "800"   # allowedSlippage
                row = "100"; row = "200"; row = "2575"; row = "60"; row = "100"
                row = "200"; row = "100"; row = "100"; row = "10"; row = "1"
                row = "1999"; row = "30"; row = "10"; row = "101"
                row = "80" if mode == "IOC" else "0"
                row = str(gap)
                lines.append(",".join(row))

    content = "\n".join(lines)
    output = io.StringIO()
    output.write(content)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype="text/csv",
        as_attachment=True,
        download_name=fileName
    )

if __name__ == "__main__":
    app.run(debug=True)
