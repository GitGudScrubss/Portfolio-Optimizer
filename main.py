import argparse
import csv
import matplotlib.pyplot as plt
import os


def read_assets(file_path):
    assets = []
    with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        print("CSV headers detected:", reader.fieldnames)
        for row in reader:
            try:
                asset = {
                    'Ticker': row['Ticker'],
                    'ExpectedReturn': float(row['ExpectedReturn(%)']) / 100,
                    'RiskScore': int(row['RiskScore(0-100)']),
                    'Price': int(float(row['Price']))
                }
                assets.append(asset)
            except (KeyError, ValueError) as e:
                print(f"Skipping row due to error: {e}")
    return assets


def knapsack(assets, capital):
    n = len(assets)
    C = capital
    dp = [[0] * (C + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(C + 1):
            price = assets[i - 1]['Price']
            value = assets[i - 1]['ExpectedReturn'] * price
            if price <= w:
                include = value + dp[i - 1][w - price]
                exclude = dp[i - 1][w]
                dp[i][w] = max(include, exclude)
            else:
                dp[i][w] = dp[i - 1][w]

    w = C
    selected = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(assets[i - 1])
            w -= assets[i - 1]['Price']

    return selected[::-1]


def apply_risk_filter(selected, risk_tolerance):
    return [a for a in selected if a['RiskScore'] <= risk_tolerance]


def sweep_and_plot(assets, capital, filename):
    risks = []
    returns = []
    for tolerance in range(0, 101, 5):
        selected = knapsack(assets, capital)
        filtered = apply_risk_filter(selected, tolerance)
        total_return = sum(a['ExpectedReturn'] * a['Price'] for a in filtered) / capital * 100 if capital > 0 else 0
        total_risk = sum(a['RiskScore'] for a in filtered)
        returns.append(total_return)
        risks.append(total_risk)

    plt.scatter(risks, returns, color='blue')
    plt.title('Efficient Frontier')
    plt.xlabel('Risk')
    plt.ylabel('Expected Return (%)')
    plt.grid(True)
    plt.savefig(filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--capital', type=int, required=True)
    parser.add_argument('--risk', type=int, required=True)
    parser.add_argument('--csv', type=str, required=True)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print("CSV file not found!")
        return

    assets = read_assets(args.csv)
    print("Assets loaded:", assets)

    selected = knapsack(assets, args.capital)
    print("After knapsack:", selected) 

    selected = apply_risk_filter(selected, args.risk)
    print("After risk filter:", selected) 

    total_cost = sum(a['Price'] for a in selected)
    total_return = sum(a['ExpectedReturn'] * a['Price'] for a in selected) / args.capital * 100 if args.capital > 0 else 0
    if selected:
        total_risk = sum(a['RiskScore'] for a in selected) / len(selected)
    else:
        total_risk = 0

    print(f"Selected {len(selected)} assets:")
    print(" ".join(a['Ticker'] for a in selected))
    print(f"Total Cost : ₹{total_cost:,}")
    print(f"Exp Return : {total_return:.1f} %")
    print(f"Risk Score : {total_risk}")

    if args.plot:
        sweep_and_plot(assets, args.capital, "frontier.png")
        print("Frontier plot saved to frontier.png")


def test_knapsack_basic():
    assets = [
        {'Ticker': 'A', 'ExpectedReturn': 0.1, 'RiskScore': 10, 'Price': 100},
        {'Ticker': 'B', 'ExpectedReturn': 0.2, 'RiskScore': 20, 'Price': 200},
    ]
    result = knapsack(assets, 200)
    assert len(result) > 0


if __name__ == '__main__':
    main()
