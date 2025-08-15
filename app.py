import csv
from datetime import datetime

def format_expiry(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    month_abbr = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
    return f"{d.day:02d}-{month_abbr[d.month-1]}-{d.year}"

def get_stg_code(ratio_str, mode):
    count = len(ratio_str.split('.'))
    if mode == "IOC":
        return 210
    if count == 2:
        return 10201
    if count == 3:
        return 10301
    if count == 4:
        return 10401
    return 10301

def generate_rows(
    legs,
    ratio_str,
    script,
    expiry_raw,
    first_strike_ce,
    first_strike_pe,
    strike_step,
    leg_gaps,
    total_strikes,
    buy_sell_pattern,
    mode,
    lot_size_val
):
    header_line = "#PID,cost,bcmp,scmp,flp,stgcode,script,lotsize,itype,expiry,otype,stkprice,ratio,buysell,pnAdd,pnMulti,bsoq,bqty,bprice,sprice,sqty,ssoq,btrQty,strQty,gap,ticksize,orderDepth,priceDepth,thshqty,allowedBiddepth,allowedSlippage,tradeGear,shortflag,isBidding,marketOrderRetries,marketOrLimitOrder,isBestbid,unhedgedActionType,TERActionType,BidWaitingType,param2,param3,param4,param5,param6,param7,param01,param02,param03,param04,param05,param06,param07,param08,param09,param10,param11,param12,param13,param14,param15,param16,param17,param18,param19,param20,param21,param22,param23,param24,param25,param26,param27,param28,param29,param30,param31,param32,param33,param34,param35,param36,param37,param38,param39,param40,param301,param302,param303,param304,param305,param306,param307,param308,param309,param310,param311,param312,param313,param314,param315,param316,param317,param318,param319,param320,param321,param322,param323,param324,param325,param326,param327,param328,param329,param330,param331,param332,param333,param334,param335,param336,param337,param338,param339,param340"
    headers = header_line.split(",")
    expiry = format_expiry(expiry_raw)
    stg_code = get_stg_code(ratio_str, mode)
    block_qtys = ["25000", "20000"]
    leg_count = len(ratio_str.split('.'))
    base_parts = buy_sell_pattern.upper().split('.')
    base_count = len(base_parts)
    gap_values = [int(g.strip()) for g in leg_gaps.split(",") if g.strip().isdigit() and int(g.strip()) > 0]

    rows = []
    rows.append(headers)
    pid = 1
    for gap in gap_values:
        for qty in block_qtys:
            # CE Legs
            otype_legs = "|".join(["CE"] * leg_count)
            exp_str = "|".join([expiry] * leg_count)
            buy_sell_str = ".".join([base_parts[j % base_count] for j in range(leg_count)])
            for i in range(total_strikes):
                prices = [first_strike_ce + i * strike_step + j * gap for j in range(leg_count)]
                row = [0]*len(headers)
                row = pid
                pid += 1
                row = stg_code
                row = script
                row = lot_size_val
                row = "-".join(["OPTIDX"]*leg_count)
                row = exp_str
                row = otype_legs
                row = "|".join(map(str,prices))
                row = ratio_str
                row = buy_sell_str
                row = 1; row = 0; row = 0; row = gap
                row = 10; row = 2; row = 2; row = 0
                row = 5; row = 200; row=2; row=1; row=1
                row=5; row=2; row=1; row=500; row=60; row=800
                row=100; row=200; row=2575; row=60; row=100; row=200
                row=100; row=100; row=10; row=1; row=1999; row=30; row=10; row=101
                rows.append(row)
            # PE Legs
            otype_legs = "|".join(["PE"] * leg_count)
            exp_str = "|".join([expiry] * leg_count)
            buy_sell_str = ".".join([base_parts[j % base_count] for j in range(leg_count)])
            for i in range(total_strikes):
                prices = [first_strike_pe - i * strike_step - j * gap for j in range(leg_count)]
                row = [0]*len(headers)
                row = pid
                pid += 1
                row = stg_code
                row = script
                row = lot_size_val
                row = "-".join(["OPTIDX"]*leg_count)
                row = exp_str
                row = otype_legs
                row = "|".join(map(str,prices))
                row = ratio_str
                row = buy_sell_str
                row = 1; row = 0; row = 0; row = gap
                row = 10; row = 2; row = 2; row = 0
                row = 5; row = 200; row=2; row=1; row=1
                row=5; row=2; row=1; row=500; row=60; row=800
                row=100; row=200; row=2575; row=60; row=100; row=200
                row=100; row=100; row=10; row=1; row=1999; row=30; row=10; row=101
                rows.append(row)
    return rows

# Example usage (run this in script):
if __name__ == "__main__":
    rows = generate_rows(
        legs=3,
        ratio_str="1.5.4",
        script="NIFTY",
        expiry_raw="2025-08-07",
        first_strike_ce=24100,
        first_strike_pe=25400,
        strike_step=50,
        leg_gaps="250",
        total_strikes=10,
        buy_sell_pattern="S.B.S",
        mode="8184",
        lot_size_val="75"
    )
    with open("NIFTY-strategy.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("CSV file generated successfully.")
