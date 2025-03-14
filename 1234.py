import requests
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# API 설정
API_KEY_DRUG = "my_drug_api_key"
BASE_URL_DRUG = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
API_KEY_MAPS = "my_maps_aip_key"

# 데이터프레임 초기화
pharmacy_data = pd.DataFrame(columns=["이름", "주소", "평점"])
address_list = []

# API 요청 함수
def get_api_response(url, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("오류", f"⚠️ API 요청 중 오류 발생: {e}")
    return None

# 약 정보 조회 함수
def get_drug_info(item_name):
    params = {"serviceKey": API_KEY_DRUG, "pageNo": "1", "numOfRows": "1", "type": "json", "itemName": item_name}
    data = get_api_response(BASE_URL_DRUG, params)
    if data and "body" in data and "items" in data["body"]:
        return data["body"]["items"][0]
    return None

# 증상 기반 약 정보 조회 함수
def get_drugs_by_symptom(symptom):
    params = {"serviceKey": API_KEY_DRUG, "pageNo": "1", "numOfRows": "5", "type": "json", "efcyQesitm": symptom}
    data = get_api_response(BASE_URL_DRUG, params)
    if data and "body" in data and "items" in data["body"]:
        return data["body"]["items"]
    return None

# 증상 기반 약 정보 검색 함수
def search_drugs_by_symptom():
    symptom = entry_symptom.get().strip()
    if not symptom:
        messagebox.showwarning("경고", "증상을 입력해주세요!")
        return

    drugs = get_drugs_by_symptom(symptom)
    result = ""
    if drugs:
        for drug in drugs:
            result += (
                f"약 이름: {drug.get('itemName', '정보 없음')}\n"
                f"효능: {drug.get('efcyQesitm', '정보 없음')}\n"
                f"제조사: {drug.get('entpName', '정보 없음')}\n"
                "-" * 40 + "\n"
            )
    else:
        result = "해당 증상에 대한 약품 정보를 찾을 수 없습니다."

    text_result_symptom.delete(1.0, tk.END)
    text_result_symptom.insert(tk.END, result)

# 약 정보 검색 버튼 동작
def search_drug():
    item_name = entry_drug.get().strip()
    if not item_name:
        messagebox.showwarning("경고", "약 이름을 입력해주세요!")
        return

    drug_info = get_drug_info(item_name)
    if drug_info:
        result = (
            f"약 이름: {drug_info.get('itemName', '정보 없음')}\n"
            f"제조사: {drug_info.get('entpName', '정보 없음')}\n"
            f"효능: {drug_info.get('efcyQesitm', '정보 없음')}\n"
            f"복용 방법: {drug_info.get('useMethodQesitm', '정보 없음')}\n"
            f"주의 사항: {drug_info.get('atpnWarnQesitm', '정보 없음')}\n"
            f"저장 방법: {drug_info.get('depositMethodQesitm', '정보 없음')}\n"
        )
    else:
        result = "해당 약품 정보를 찾을 수 없습니다."

    text_result_drug.delete(1.0, tk.END)
    text_result_drug.insert(tk.END, result)

# 주변 약국 검색 함수
def search_pharmacy():
    address = entry_address_pharmacy.get().strip()
    if not address:
        messagebox.showwarning("경고", "주소를 입력해주세요!")
        return

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"{address} 약국", "key": API_KEY_MAPS}

    data = get_api_response(url, params)
    if not data or "results" not in data:
        messagebox.showerror("오류", "약국 정보를 불러오지 못했습니다.")
        return

    # 검색 결과 표시
    tree_pharmacy.delete(*tree_pharmacy.get_children())
    for place in data["results"][:10]:  
        name = place.get("name", "이름 없음")
        address = place.get("formatted_address", "주소 없음")
        rating = place.get("rating", "평점 없음")
        tree_pharmacy.insert("", "end", values=(name, address, rating))

# UI 설정
root = tk.Tk()
root.title("약 정보 및 서비스")
root.geometry("800x700")

tab_control = ttk.Notebook(root)

# 📌 약 정보 탭
tab_drug = ttk.Frame(tab_control)
tab_control.add(tab_drug, text="약 정보 조회")

label_drug = tk.Label(tab_drug, text="약 이름을 입력하세요:")
label_drug.pack(pady=5)
entry_drug = tk.Entry(tab_drug, width=50)
entry_drug.pack(pady=5)
btn_search_drug = tk.Button(tab_drug, text="검색", command=search_drug)
btn_search_drug.pack(pady=5)
text_result_drug = tk.Text(tab_drug, wrap=tk.WORD, height=20)
text_result_drug.pack(pady=5)

# 📌 증상 기반 약 조회 탭
tab_symptom = ttk.Frame(tab_control)
tab_control.add(tab_symptom, text="증상 기반 약 조회")

label_symptom = tk.Label(tab_symptom, text="증상을 입력하세요:")
label_symptom.pack(pady=5)
entry_symptom = tk.Entry(tab_symptom, width=50)
entry_symptom.pack(pady=5)
btn_search_symptom = tk.Button(tab_symptom, text="검색", command=search_drugs_by_symptom)
btn_search_symptom.pack(pady=5)
text_result_symptom = tk.Text(tab_symptom, wrap=tk.WORD, height=20)
text_result_symptom.pack(pady=5)

# 📌 주변 약국 검색 탭
tab_pharmacy = ttk.Frame(tab_control)
tab_control.add(tab_pharmacy, text="주변 약국 검색")

label_address = tk.Label(tab_pharmacy, text="검색할 주소를 입력하세요:")
label_address.pack(pady=5)
entry_address_pharmacy = tk.Entry(tab_pharmacy, width=50)
entry_address_pharmacy.pack(pady=5)
btn_search_pharmacy = tk.Button(tab_pharmacy, text="검색", command=search_pharmacy)
btn_search_pharmacy.pack(pady=5)

tree_pharmacy = ttk.Treeview(tab_pharmacy, columns=["이름", "주소", "평점"], show="headings")
tree_pharmacy.heading("이름", text="이름")
tree_pharmacy.heading("주소", text="주소")
tree_pharmacy.heading("평점", text="평점")
tree_pharmacy.pack(fill="both", expand=True, pady=5)

tab_control.pack(expand=1, fill="both")

# 진료 주소 추가 함수
def add_address():
    address = entry_address.get().strip()
    if not address:
        messagebox.showwarning("경고", "주소를 입력해주세요!")
        return

    # 주소 리스트에 추가
    address_list.append(address)
    
    # Treeview에 추가
    tree_address.insert("", "end", values=(address,))
    
    # 입력 필드 초기화
    entry_address.delete(0, tk.END)

# 진료 주소 관리 탭
tab_address = ttk.Frame(tab_control)
tab_control.add(tab_address, text="진료 주소 관리")

address_frame = tk.Frame(tab_address)
address_frame.pack(pady=5)

label_address_input = tk.Label(address_frame, text="진료 희망 주소:")
label_address_input.grid(row=0, column=0, padx=5)
entry_address = tk.Entry(address_frame, width=40)
entry_address.grid(row=0, column=1, padx=5)
btn_add_address = tk.Button(address_frame, text="추가", command=add_address)  # 수정됨
btn_add_address.grid(row=0, column=2, padx=5)

tree_address = ttk.Treeview(tab_address, columns=["주소"], show="headings")
tree_address.heading("주소", text="주소")
tree_address.column("주소", width=400)
tree_address.pack(fill="both", expand=True, pady=5)

root.mainloop()
