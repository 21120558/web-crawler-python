from requests_html import HTMLSession
import pandas as pd

session = HTMLSession()

URL_ID = 'https://tiki.vn/api/v2/products?limit={limit}&include=advertisement&aggregations=2&trackity_id=34308664-a1c4-6840-fcc6-ad1c658360fc&q={keyword}&page={page}'
URL_INFO = 'https://tiki.vn/api/v2/products/{id_product}'
URL_REVIEW = 'https://tiki.vn/api/v2/reviews?limit=1000&include=comments,contribute_info&sort=score%7Cdesc,id%7Cdesc,stars%7Call&page={page}&spid={spid}&product_id={product_id}'

# Hàm lấy các ID sản phẩm theo keyword và số lượng (quantity)
def CrawlIDProduct(keyword, quantity):
    products = {"product_id": [], "spid": []}
    count = 0

    limit = 100
    limit_page = quantity // (limit + 1)

    print("-" * 100)
    print("Cac duong dan chua id san pham.")

    for i in range(1, limit_page+2):

        data = session.get(URL_ID.format(limit=limit, keyword=keyword, page=i)).json()
        print(URL_ID.format(limit=limit, keyword=keyword, page=i))

        for product in data["data"]:
            products["product_id"].append(product["id"])
            products["spid"].append(product["seller_product_id"])
            count += 1
            if count % 100 == 0 or count == quantity:
                break

    return products

# Hàm lấy cụ thể các thông tin sản phẩm theo ID đã lấy được
def CrawlInfoProduct(products):
    info_products = {
                        "ID":                   [],
                        "Ten san pham" :        [],
                        "URL":                  [],
                        "Gia hien tai":         [],
                        "Gia goc":              [],
                        "So sao trung binh":    [],
                        "So luong danh gia":    [],
                        "Thuong hieu":          [],
                        "Don vi ban":           [],
                        "Da ban":               [],
                     }

    print("-" * 100)
    print("Cac duong dan chua thong tin san pham.")

    # Hàm for thứ nhất sẽ trích xuất từng id sản phẩm trong list products đã lấy được trước đó
    for id_product in products["product_id"]:
        # Hàm session.get lấy thông tin từ đường dẫn URL_INFO
        info_product = session.get(URL_INFO.format(id_product=id_product)).json()
        print(URL_INFO.format(id_product=id_product))

        info_products["ID"].append(info_product["id"])

        # Trong đường dẫn có thể có những element không xuất hiện như đã lập trình
        # Vì vậy cặp lệnh try - except được sử dụng để hạn chế tình trạng đó
        # Nếu không tồn tại thì ta sẽ chèn một ký tự rỗng vào vị trí
        try:
            info_products["Ten san pham"].append(info_product["name"])
        except:
            info_products["Ten san pham"].append(" ")

        try:
            info_products["URL"].append("https://tiki.vn/" + info_product["url_path"])
        except:
            info_products["URL"].append(" ")

        try:
            info_products["Gia hien tai"].append(info_product["price"])
        except:
            info_products["Gia hien tai"].append(" ")

        try:
            info_products["Gia goc"].append(info_product["original_price"])
        except:
            info_products["Gia goc"].append(" ")

        try:
            info_products["So sao trung binh"].append(info_product["rating_average"])
        except:
            info_products["So sao trung binh"].append(" ")

        try:
            info_products["So luong danh gia"].append(info_product["review_count"])
        except:
            info_products["So luong danh gia"].append(" ")

        try:
            info_products["Thuong hieu"].append(info_product["brand"]["name"])
        except:
            info_products["Thuong hieu"].append(" ")

        try:
            info_products["Don vi ban"].append(info_product["current_seller"]["name"])
        except:
            info_products["Don vi ban"].append(" ")

        try:
           info_products["Da ban"].append(info_product["quantity_sold"]["value"])
        except:
            info_products["Da ban"].append(" ")

    return info_products

# Hàm lấy chi tiết các đánh giá về sản phẩm theo ID đã lấy được
def CrawlReviewProduct(products, info_products):
    # Khai báo list review_products chứa các thông tin chi tiết của các đánh giá
    review_products =   {
                            "ID san pham":      [],
                            "Trang thai":       [],
                            "Binh luan":        [],
                            "So sao":           [],
                            "Thoi diem gui":    [],
                            "Ten nguoi dung":   [],
                            "Da viet":          [],
                            "Duoc cam on":      [],
                        }

    print("-" * 100)
    print("Cac duong dan chua danh gia san pham.")

    # Hàm for thứ nhất sẽ truy cập từng sản phẩm và từ đó có được các đánh giá
    # URL_REVIEW chứa các tham số spid, product_id và page, các thông tin này sẽ được lấy từ list products đã được tạo trước đó
    for spid, product_id, quantity_review in zip(products["spid"], products["product_id"], info_products["So luong danh gia"]):
        limit_page = quantity_review // 1001

        # Hàm for thứ hai sẽ truy cập từng trang
        for page in range(1, limit_page + 2):
            review_product = session.get(URL_REVIEW.format(spid=spid, product_id=product_id, page=page)).json()
            print(URL_REVIEW.format(spid=spid, product_id=product_id, page=page))

            # Hàm for thứ ba lồng trong hàm for thứ nhất sẽ lấy từng thông tin đánh giá và lưu trữ vào list review_products
            for i, review in enumerate(review_product["data"]):
                if i == quantity_review:
                    break

                review_products["ID san pham"].append(product_id)

                try:
                    review_products["Trang thai"].append(review["title"])
                except:
                    review_products["Trang thai"].append(" ")

                try:
                    review_products["Binh luan"].append(review["content"])
                except:
                    review_products["Binh luan"].append(" ")

                try:
                    review_products["So sao"].append(review["rating"])
                except:
                    review_products["So sao"].append(" ")

                try:
                    review_products["Thoi diem gui"].append(review["timeline"]["review_created_date"])
                except:
                    review_products["Thoi diem gui"].append(" ")

                try:
                    review_products["Ten nguoi dung"].append(review["created_by"]["name"])
                except:
                    review_products["Ten nguoi dung"].append(" ")

                try:
                    review_products["Da viet"].append(review["created_by"]["contribute_info"]["summary"]["total_review"])
                except:
                    review_products["Da viet"].append(0)

                try:
                    review_products["Duoc cam on"].append(review["created_by"]["contribute_info"]["summary"]["total_thank"])
                except:
                    review_products["Duoc cam on"].append(0)

    return review_products

def BrandFilter(df_info):
    i = 0
    brands = []
    print(df_info["Thuong hieu"].drop_duplicates(keep='first'))
    print("Nhap nhung hang ban muon chon va ket thuc bang tu khoa \"none\" hoac lay tat ca bang tu khoa \"All\" ")
    while (True):
        brands.append(input())
        if brands[i] == "All":
            return df_info
        if brands[i] == "none":
            break
        i += 1
    sr_brand = pd.Series(brands)
    df_info = df_info[df_info["Thuong hieu"].isin(sr_brand)]

    print("-" * 100)
    return df_info

def PriceFilter(df_info):
    print("Gia cua cac san pham nam trong khoang:", df_info["Gia hien tai"].min(), "toi", df_info["Gia hien tai"].max())
    print("Nhap khoang gia ban muon lay hoac nhap \"All\" neu muon lay tat ca: ")
    min = input("Min: ")
    if min == "All":
        min = df_info["Gia hien tai"].min()
        max = df_info["Gia hien tai"].max()
    else:
        min = int(min)
        max = int(input("Max: "))

    df_info = df_info[(min <= df_info["Gia hien tai"]) & (df_info["Gia hien tai"] <= max)]

    print("-" * 100)
    return df_info

def AvgRatingFilter(df_info):
    print("So sao trung binh cua cac san pham nam trong khoang:", df_info["So sao trung binh"].min(), "toi",
          df_info["So sao trung binh"].max())
    print("Nhap khoang gia ban muon lay hoac nhap \"All\" neu muon lay tat ca: ")
    min = input("Min: ")
    if min == "All":
        min = df_info["So sao trung binh"].min()
        max = df_info["So sao trung binh"].max()
    else:
        min = float(min)
        max = float(input("Max: "))

    df_info = df_info[(min <= df_info["So sao trung binh"]) & (df_info["So sao trung binh"] <= max)]

    print("-" * 100)
    return df_info

def RatingFilter(df_review):
    i = 0
    ratings = []
    print(df_review["So sao"].drop_duplicates(keep='first'))
    print("Nhap nhung so sao cua nhung danh gia ban muon lay va ket thuc bang -1 hoac nhap tu khoa \"All\" de lay tat ca")
    while (True):
        rating = input()
        if rating == "All":
            return df_review

        ratings.append(int(rating))
        if ratings[i] == -1:
            break
        i += 1
    sr_rating = pd.Series(ratings)
    df_review = df_review[df_review["So sao"].isin(sr_rating)]

    print("-" * 100)
    return df_review

def FilterInfoData(info_products):
    # Tạo Dataframe từ thư viện pandas lưu trữ các thông tin sản phẩm và đánh giá
    df_info = pd.DataFrame(info_products)

    df_info = BrandFilter(df_info)
    df_info = PriceFilter(df_info)
    df_info = AvgRatingFilter(df_info)

    return df_info

def FilterReviewData(review_products, df_info):
    df_review = pd.DataFrame(review_products)

    sr_id = pd.Series(df_info["ID"])
    df_review = df_review[df_review["ID san pham"].isin(sr_id)]

    df_review = RatingFilter(df_review)
    return df_review

def ConvertKeyword(keyword):
    for i in range(0, len(keyword)):
        if keyword[i] == " ":
            keyword[i] = "+"

    return keyword


# Input: Keyword muốn tìm kiếm và số lượng sản phẩm
keyword = input("Nhap keyword cua san pham can Crawl: ").replace(" ", "+")

quantity = int(input("Nhap so luong san pham: "))

# Thu thập ID
products = CrawlIDProduct(keyword, quantity)

# Thu thập thông tin cụ thể
info_products = CrawlInfoProduct(products)

# Thu thập toàn bộ review các sản phẩm
review_products = CrawlReviewProduct(products, info_products)

#Lọc dữ liệu và xuất file
df_info = FilterInfoData(info_products)
df_review = FilterReviewData(review_products, df_info)

df_info.to_csv("info.csv", index=False)
df_review.to_csv("review.csv", index=False)
