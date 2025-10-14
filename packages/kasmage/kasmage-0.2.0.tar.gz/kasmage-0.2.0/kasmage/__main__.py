import argparse

from . import __version__
from . import sentry
from . import receipts as receipts_mod

from importlib.metadata import version, PackageNotFoundError

# -------- Art --------
FROG_KASMAGE = r"""
                        
                     .@@@.                       
                    @*=-@#                       
                   @  ==%@                       
                  %+===+*%@                      
                 @#= -=+##@.                    
               :#+=+.=++=*%@                    
            =%%@@+++.=*+ :%@          ] .  m,  m, .mm  m,  mm  m, 
           @@#==+****@@@@@@@@@@@      ].` ' ] ] ' ]]] ' ] ]`T ]`] 
             %.@@@@@@@@@@@%%%@@@      ]T  ."T  "\ ]]] ."T ] ] ]"" 
            .+*+.    =@@# %-          ] \ 'mT 'm/ ]]] 'mT 'bT 'b/ 
            %*----------   -+                              ,]
             +               -%                            '`
              @             %%=@:               
            %:%       %   @     @@              
            -*@ #     % = @      @              
           +%*@ *@    % @=:+%*  @:              
          %@@=%@ .%@@.# @@ .  %@=               
                            ...                     
"""

# Package version
try:
    KASMAGE_VERSION = version("kasmage")
except PackageNotFoundError:
    KASMAGE_VERSION = "0.0.0-dev"

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-V", "--version", action="store_true", help="print version and exit")
    args, remaining = parser.parse_known_args()

    if args.version:
        print(f"kasmage {KASMAGE_VERSION}")
        return 0
    
    print(FROG_KASMAGE)

    p = argparse.ArgumentParser(description="Kasmage — Kaspa tx logger (historical or live)")
    p.add_argument("--address", required=True, help="kaspa:...")
    p.add_argument("--interval", type=int, default=10, help="poll seconds (live mode)")
    p.add_argument("--page-size", type=int, default=sentry.PAGE_SIZE, help="transactions per page")
    p.add_argument("--historical", action="store_true", help="print ALL historical tx and exit")
    p.add_argument("-V", "--version", action="store_true", help="print version and exit")

    # Receipt toggles
    p.add_argument("--receipts", action="store_true", help="write a receipt per new tx (live mode)")
    p.add_argument("--receipts-dir", default="receipts", help="directory for receipts")
    p.add_argument("--receipt-format", choices=["txt", "json"], default="txt", help="receipt format")

    args = p.parse_args()

    if args.version:
        print(__version__)
        return 0

    if args.historical:
        return sentry.run_historical(args.address, page_size=args.page_size)

    # Build the on_tx handler
    def on_tx(txid: str, amount_kas: float, time_ms, tx_dict):
        # Always print
        print(f"✨👀 I scry with my amphibian eye a tx: {amount_kas:.8f} KAS | txid: {txid} | {sentry.format_time_ms(time_ms)}")
        # Optionally write receipt
        if args.receipts:
            path = receipts_mod.write_receipt(
                args.receipts_dir,
                address=args.address,
                txid=txid,
                amount_kas=amount_kas,
                time_ms=time_ms,
                fmt=args.receipt_format,
            )
            print(f"📜 Behold! Another slimy scroll of coinage joins the spellbook: {path}")

    return sentry.run_live(
        args.address,
        interval=args.interval,
        page_size=args.page_size,
        on_tx=on_tx,
    )

if __name__ == "__main__":
    raise SystemExit(main())