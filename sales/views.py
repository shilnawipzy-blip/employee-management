from django.shortcuts import render, redirect
import pandas as pd
import io


def sales_list(request):
    return render(
        request,
        "sales_list.html",
        {
            "report_type": request.session.get("report_type", ""),
            "total_sales": request.session.get("total_sales", 0),
            "total_quantity": request.session.get("total_quantity", 0),
            "total_invoices": request.session.get("total_invoices", 0),
            "total_orders": request.session.get("total_orders", 0),
            "total_items": request.session.get("total_items", 0),
            "item_totals": request.session.get("item_totals", {}),
            "category_totals": request.session.get(
                "category_totals", {}
            ),
            "party_totals": request.session.get(
                "party_totals", {}
            ),
            "ledger_totals": request.session.get(
                "ledger_totals", {}
            ),
            "error_message": request.session.pop(
                "error_message", ""
            ),
        },
    )


def sales_upload(request):

    if request.method == "POST":

        file = request.FILES.get("excel_file")

        if not file:
            request.session["error_message"] = (
                "Please select an Excel or CSV file."
            )
            return render(
                request,
                "sales_upload.html"
            )

        try:
            file_data = file.read()

            if file.name.lower().endswith(".csv"):

                raw_df = pd.read_csv(
                    io.BytesIO(file_data),
                    header=None
                )

            else:

                raw_df = pd.read_excel(
                    io.BytesIO(file_data),
                    header=None
                )

            possible_headers = [
                {"Party Name", "Invoice No.", "Transaction Type", "Total Amount"},
                {"HEAD OF ACCOUNT", "DR AMOUNT", "CR AMOUNT"},
                {"InvNo", "Customer", "Qty", "GrossAmount"},
                {"Item Name", "Qty", "Unit Price ($)"},
                {"Itemname", "Qty", "Total"},
                {"Item", "Total Amount"},
            ]

            df = None
            for index, row in raw_df.iterrows():

                values = set(
                    row.astype(str)
                    .str.strip()
                    .tolist()
                )

                for headers in possible_headers:

                    if headers.issubset(values):

                        if file.name.lower().endswith(".csv"):

                            df = pd.read_csv(
                                io.BytesIO(file_data),
                                header=index
                            )

                        else:

                            df = pd.read_excel(
                                io.BytesIO(file_data),
                                header=index
                            )

                        break

                if df is not None:
                    break

            if df is None:
                request.session["error_message"] = (
                    "Unsupported file format. "
                    "Please upload a valid Excel or CSV sales report."
                )

                return render(
                    request,
                    "sales_upload.html"
                )
            df = df.dropna(how="all")

            df.columns = (
                df.columns
                .astype(str)
                .str.strip()
            )

            total_sales = 0
            total_quantity = 0
            total_invoices = 0
            total_orders = 0
            total_items = 0

            item_totals = {}
            category_totals = {}
            party_totals = {}
            ledger_totals = {}

            report_type = ""
            if (
                "Item" in df.columns
                and "Total Amount" in df.columns
            ):

                report_type = "Restaurant Sales"

                df["Total Amount"] = (
                    df["Total Amount"]
                    .astype(str)
                    .str.replace("₹", "", regex=False)
                    .str.replace("$", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df["Total Amount"] = pd.to_numeric(
                    df["Total Amount"],
                    errors="coerce"
                ).fillna(0)

                if "Status" in df.columns:

                    df = df[
                        df["Status"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        == "completed"
                    ]

                item_totals = (
                    df.groupby("Item")["Total Amount"]
                    .sum()
                    .to_dict()
                )

                if "Category" in df.columns:

                    category_totals = (
                        df.groupby("Category")["Total Amount"]
                        .sum()
                        .to_dict()
                    )

                total_sales = df["Total Amount"].sum()

                total_quantity = (
                    pd.to_numeric(
                        df["Quantity"],
                        errors="coerce"
                    ).sum()
                    if "Quantity" in df.columns
                    else 0
                )

                if "Invoice No" in df.columns:

                    total_invoices = (
                        df["Invoice No"]
                        .nunique()
                    )

                if "Order ID" in df.columns:

                    total_orders = (
                        df["Order ID"]
                        .nunique()
                    )

                else:

                    total_orders = len(df)

                total_items = df["Item"].nunique()
            elif (
                "Item Name" in df.columns
                and "Qty" in df.columns
                and "Unit Price ($)" in df.columns
            ):

                report_type = "Restaurant Sales"

                df["Qty"] = pd.to_numeric(
                    df["Qty"],
                    errors="coerce"
                ).fillna(0)

                df["Unit Price ($)"] = pd.to_numeric(
                    df["Unit Price ($)"],
                    errors="coerce"
                ).fillna(0)

                df["Amount"] = (
                    df["Qty"]
                    * df["Unit Price ($)"]
                )

                if "Status" in df.columns:

                    df = df[
                        df["Status"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        == "completed"
                    ]

                item_totals = (
                    df.groupby("Item Name")["Amount"]
                    .sum()
                    .to_dict()
                )

                if "Category" in df.columns:

                    category_totals = (
                        df.groupby("Category")["Amount"]
                        .sum()
                        .to_dict()
                    )

                total_sales = df["Amount"].sum()

                total_quantity = df["Qty"].sum()

                if "Invoice No" in df.columns:

                    total_invoices = (
                        df["Invoice No"]
                        .nunique()
                    )

                if "Order ID" in df.columns:

                    total_orders = (
                        df["Order ID"]
                        .nunique()
                    )

                else:

                    total_orders = len(df)

                total_items = df["Item Name"].nunique()
            elif (
                "Itemname" in df.columns
                and "Qty" in df.columns
                and "Total" in df.columns
            ):

                report_type = "Garments Sales"
                df = df[
                    df["Itemname"].notna()
                ]

                df["Qty"] = pd.to_numeric(
                    df["Qty"],
                    errors="coerce"
                ).fillna(0)

                df["Total"] = (
                    df["Total"]
                    .astype(str)
                    .str.replace("₹", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df["Total"] = pd.to_numeric(
                    df["Total"],
                    errors="coerce"
                ).fillna(0)

                item_totals = (
                    df.groupby("Itemname")["Total"]
                    .sum()
                    .to_dict()
                )

                total_sales = df["Total"].sum()

                total_quantity = df["Qty"].sum()

                total_orders = len(df)

                total_items = df["Itemname"].nunique()
            elif (
                "InvNo" in df.columns
                and "Customer" in df.columns
                and "Qty" in df.columns
                and "GrossAmount" in df.columns
            ):

                report_type = "Invoice Sales Report"
                df = df[
                    df["InvNo"].notna()
                ]

                df["Qty"] = pd.to_numeric(
                    df["Qty"],
                    errors="coerce"
                ).fillna(0)

                df["GrossAmount"] = (
                    df["GrossAmount"]
                    .astype(str)
                    .str.replace("₹", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df["GrossAmount"] = pd.to_numeric(
                    df["GrossAmount"],
                    errors="coerce"
                ).fillna(0)

                party_totals = (
                    df.groupby("Customer")["GrossAmount"]
                    .sum()
                    .to_dict()
                )

                total_sales = (
                    df["GrossAmount"].sum()
                )

                total_quantity = (
                    df["Qty"].sum()
                )

                total_invoices = (
                    df["InvNo"].nunique()
                )

                total_orders = total_invoices

                total_items = (
                    df["Customer"].nunique()
                )
                
            elif (
                "HEAD OF ACCOUNT" in df.columns
                and "DR AMOUNT" in df.columns
                and "CR AMOUNT" in df.columns
            ):

                report_type = "Ledger Statement"

                df = df[
                    df["HEAD OF ACCOUNT"].notna()
                ]

                df["DR AMOUNT"] = (
                    df["DR AMOUNT"]
                    .astype(str)
                    .str.replace("₹", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df["CR AMOUNT"] = (
                    df["CR AMOUNT"]
                    .astype(str)
                    .str.replace("₹", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df["DR AMOUNT"] = pd.to_numeric(
                    df["DR AMOUNT"],
                    errors="coerce"
                ).fillna(0)

                df["CR AMOUNT"] = pd.to_numeric(
                    df["CR AMOUNT"],
                    errors="coerce"
                ).fillna(0)

                # Sales = SALES account debit amount
                sales_df = df[
                    df["HEAD OF ACCOUNT"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    == "SALES"
                ]

                total_sales = sales_df["DR AMOUNT"].sum()

                # Total quantity is not available in ledger
                total_quantity = 0

                # Total sales orders
                if "REF NO" in sales_df.columns:
                    total_orders = sales_df["REF NO"].nunique()
                else:
                    total_orders = len(sales_df)

                # Ledger doesn't have invoice numbers
                total_invoices = 0

                # Unique accounts
                total_items = df["HEAD OF ACCOUNT"].nunique()

                ledger_totals = (
                    df.groupby("HEAD OF ACCOUNT")
                    .agg({
                        "DR AMOUNT": "sum",
                        "CR AMOUNT": "sum"
                    })
                    .to_dict("index")
                )
            elif (
                "Party Name" in df.columns
                and "Total Amount" in df.columns
                and "Transaction Type" in df.columns
            ):

                report_type = "Party Sales Report"

                # Remove final total row
                df = df[
                    df["Party Name"].notna()
                ]

                df["Total Amount"] = (
                    df["Total Amount"]
                    .astype(str)
                    .str.replace("₹", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df["Total Amount"] = pd.to_numeric(
                    df["Total Amount"],
                    errors="coerce"
                ).fillna(0)

                party_totals = (
                    df.groupby("Party Name")["Total Amount"]
                    .sum()
                    .to_dict()
                )

                category_totals = (
                    df.groupby("Transaction Type")[
                        "Total Amount"
                    ]
                    .sum()
                    .to_dict()
                )

                total_sales = (
                    df["Total Amount"].sum()
                )

                total_orders = len(df)

                total_items = (
                    df["Party Name"].nunique()
                )

                if "Invoice No." in df.columns:

                    total_invoices = (
                        df["Invoice No."]
                        .nunique()
                    )
            else:

                request.session["error_message"] = (
                    "Unsupported Excel format. "
                    "Please upload a valid sales report."
                )

                return render(
                    request,
                    "sales_upload.html"
                )
            request.session["report_type"] = report_type
            request.session["total_sales"] = float(
                total_sales
            )
            request.session["total_quantity"] = float(
                total_quantity
            )
            request.session["total_invoices"] = int(
                total_invoices
            )
            request.session["total_orders"] = int(
                total_orders
            )
            request.session["total_items"] = int(
                total_items
            )

            request.session["item_totals"] = {
                str(key): float(value)
                for key, value in item_totals.items()
            }

            request.session["category_totals"] = {
                str(key): float(value)
                for key, value in category_totals.items()
            }

            request.session["ledger_totals"] = {
                str(account): {
                    "debit": float(values["DR AMOUNT"]),
                    "credit": float(values["CR AMOUNT"]),
                }
                 for account, values in ledger_totals.items()
            }

            return redirect("sales_list")

        except Exception:

            request.session["error_message"] = (
                "Unable to process the file. "
                "Please check the file and try again."
            )

            return render(
                request,
                "sales_upload.html"
            )

    return render(
        request,
        "sales_upload.html"
    )