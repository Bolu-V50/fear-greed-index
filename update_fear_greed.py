import requests
import json
from datetime import datetime

def fetch_fear_greed_data():
    """获取恐惧贪婪指数数据"""
    url = "https://api.alternative.me/fng/?limit=90"
    
    try:
        response = requests.get(url)
        data = response.json()
        return data['data']
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def generate_pine_script(data_points):
    """生成Pine Script代码"""
    
    pine_template = '''//@version=5
indicator("恐惧贪婪指数 (每日更新)", overlay=false)

// 更新时间: {update_time}

var float[] values = array.new_float()
var int[] dates = array.new_int()

if barstate.isfirst
{data_init}

getValue() =>
    result = 50.0
    currentDate = timestamp(year, month, dayofmonth)
    for i = 0 to array.size(dates) - 1
        if array.get(dates, i) == currentDate
            result := array.get(values, i)
            break
    result

fgi = getValue()
ma7 = ta.sma(fgi, 7)
ma30 = ta.sma(fgi, 30)

getColor(v) =>
    v <= 25 ? color.red : v <= 45 ? color.orange : v <= 55 ? color.yellow : v <= 75 ? color.green : color.rgb(0,200,0)

plot(fgi, "Fear & Greed", color=getColor(fgi), linewidth=3)
plot(ma7, "MA7", color=color.blue, linewidth=1)
plot(ma30, "MA30", color=color.purple, linewidth=1)

bgcolor(fgi <= 25 ? color.new(color.red, 95) : na)
bgcolor(fgi > 25 and fgi <= 45 ? color.new(color.orange, 95) : na)
bgcolor(fgi > 45 and fgi <= 55 ? color.new(color.yellow, 95) : na)
bgcolor(fgi > 55 and fgi <= 75 ? color.new(color.green, 95) : na)
bgcolor(fgi > 75 ? color.new(color.green, 90) : na)

hline(25, "极度恐惧", color=color.red, linestyle=hline.style_dotted)
hline(45, "恐惧", color=color.orange, linestyle=hline.style_dotted)
hline(55, "中性", color=color.gray, linestyle=hline.style_dotted)
hline(75, "贪婪", color=color.green, linestyle=hline.style_dotted)
hline(0, "Min", color=color.gray)
hline(100, "Max", color=color.gray)

var table infoTable = table.new(position.top_right, 2, 4)
if barstate.islast
    table.cell(infoTable, 0, 0, "当前指数", bgcolor=color.navy, text_color=color.white)
    table.cell(infoTable, 1, 0, str.tostring(fgi, "#"), bgcolor=getColor(fgi), text_color=color.white)
    table.cell(infoTable, 0, 1, "7日均线", text_color=color.blue)
    table.cell(infoTable, 1, 1, str.tostring(ma7, "#"), text_color=color.blue)
    table.cell(infoTable, 0, 2, "30日均线", text_color=color.purple)
    table.cell(infoTable, 1, 2, str.tostring(ma30, "#"), text_color=color.purple)
    table.cell(infoTable, 0, 3, "更新日期", text_color=color.gray)
    table.cell(infoTable, 1, 3, "{update_date}", text_color=color.gray)
'''
    
    data_init = []
    for item in data_points:
        timestamp = int(item['timestamp'])
        dt = datetime.fromtimestamp(timestamp)
        value = item['value']
        data_init.append(f'    array.push(dates, timestamp({dt.year}, {dt.month}, {dt.day}))')
        data_init.append(f'    array.push(values, {value})')
    
    final_code = pine_template.format(
        update_time=datetime.now().strftime('%Y-%m-%d %H:%M'),
        update_date=datetime.now().strftime('%Y-%m-%d'),
        data_init='\n'.join(data_init)
    )
    
    return final_code

def main():
    print("Fetching Fear and Greed Index data...")
    data = fetch_fear_greed_data()
    
    if data:
        print(f"Successfully fetched {len(data)} data points")
        
        # 保存JSON数据
        with open('fear_greed_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        # 生成并保存Pine Script
        pine_code = generate_pine_script(data)
        with open('fear_greed_index.pine', 'w', encoding='utf-8') as f:
            f.write(pine_code)
        
        print("Files generated successfully!")
        print(f"Latest Fear & Greed Index: {data[0]['value']} ({data[0]['value_classification']})")
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    main()
