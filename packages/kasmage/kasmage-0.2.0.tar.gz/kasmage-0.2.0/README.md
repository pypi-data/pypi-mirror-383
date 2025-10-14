<!-- ![alt text](assets/kasmage_alt.png "Kasmage") -->
<!-- ![alt text](assets/kasmage.png "Kasmage") -->

<!-- 
I'm new to the crypto space and this might not be anthing game-changing but
it's a fun little project to work on. If you have ideas for new features, 
please open a feature request (Issue).  If you’ve built something cool, feel 
free to fork the repo and submit a PR!  
 -->

<!-- 
Flubs Ompi is the official name of the Kasmage frog. Follow me on X @evofcl
to suggest cool new epithets! Also, if you're a graphic designer, send me a
.png of your frog design and I might just feature it!
-->

<table>
<tr>
<td width="160">
  <img src="assets/kasmage.png" width="160" alt="Flubs Ompi, DAG Mage"/>
</td>
<td>
  <h1>Kasmage</h1>
  <p>
    🐸 Kasmage is a whimsical, lightweight frog-wizard themed CLI that monitors a Kaspa address for transactions.<br>
    It can print all historical transactions or watch for new ones in real time.
    <i>Official mascot:</i> <b>Flubs Ompi, DAG Mage</b>.
  </p>
</td>
</tr>
</table>

## Quickstart (Install & Run)

Clone the repo, build the wheel, and install locally:
```bash
git clone https://github.com/yourname/kasmage.git
cd kasmage
poetry build
pip install --force-reinstall dist/kasmage-0.1.0-py3-none-any.whl
```
Now run:
```bash
kasmage --address kaspa:yourkaspaaddresshere
```

## Features

- **Live mode**: watch an address and get notified when new transactions confirm  
- **Historical mode**: print all confirmed transactions (oldest → newest) and exit  
- **Receipts (new!)**: automatically save each detected transaction as a TXT or JSON eceipt for record-keeping  
- Compatible with Kaspa mainnet addresses (`kaspa:...`)  

## Installation

For now, clone the repo and install with Poetry:
```bash
git clone https://github.com/yourname/kasmage.git
cd kasmage
poetry install
```

## Usage

Watch new transactions (default live mode)
```bash
kasmage --address kaspa:qpwhk9yja6n2l73enwl62s2u52c7u87mjkh4mwhyeueum660ght4735mlsas5
```
Output example:
```bash
🐸🔮 Peering into the orb... (Ctrl+C to stop)
✨👀 I scry with my amphibian eye a tx: 40.00000000 KAS | b7d51e1d29b... | 2025-10-13 07:28:45 UTC
```
Print all past transactions
```bash
kasmage --address kaspa:qpwhk9yja6n2l73enwl62s2u52c7u87mjkh4mwhyeueum660ght4735mlsas5 --historical
```
Output example:
```bash
📜 100.00000000 KAS | txid: 6c7a0b8473b... | 2025-10-12 02:43:09 UTC
📜 200.11837708 KAS | txid: 1a3ede08005... | 2025-10-12 01:21:17 UTC
```

## Options
- -h, --help: All this info pretty much
- --address (required): Kaspa address to monitor
- --interval: Poll interval in seconds (default: 10)
- --page-size: Number of tx per API page (default: 50)
- --historical: Print all confirmed tx and exit
- -V, --version: Print version and exit
- --receipts: Write a recipt per new tx (live mode)
- --receipts-dir: Directory for receipts
- --receipt-format: Self explanitory

## License
MIT © Ethan Villalobos