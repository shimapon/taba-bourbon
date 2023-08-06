import pandas as pd
import matplotlib.pyplot as plt
import os

def create_weekly_graph(df):
    # グラフの大きさを指定
    plt.figure(figsize=(12, 8))

    # 各平均時間に対してプロット
    plt.plot(df['Week'], df['Open to Merge'], label="Open to Merge", marker='o')
    plt.plot(df['Week'], df['Open to Review Start'], label="Open to Review Start", marker='o')
    plt.plot(df['Week'], df['Review Start to Merge'], label="Review Start to Merge", marker='o')

    # グラフのタイトル、x軸y軸のラベル、凡例の設定
    plt.title('Weekly Averages')
    plt.xlabel('Week')
    plt.ylabel('Average Hours')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()

    # 画像として保存
    img_path = 'weekly_averages.png'  # 直接ファイル名を指定して相対パスを作成
    plt.savefig(img_path)
    plt.close()

    return img_path

def write_to_html(all_daily_data, all_weekly_data):
    df_daily = pd.DataFrame(all_daily_data)
    df_weekly = pd.DataFrame(all_weekly_data)
    img_path = create_weekly_graph(df_weekly)
    
    with open('results.html', 'w') as f:
        f.write("<h2>Daily Data</h2>")
        f.write(df_daily.to_html(index=False))
        f.write("<h2>Weekly Data</h2>")
        f.write(df_weekly.to_html(index=False))
        f.write(f"<h2>Weekly Averages Graph</h2><img src='{img_path}' alt='Weekly Averages Graph'>")
