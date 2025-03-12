import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import re

# Danh sách quy tắc
rules = [
    lambda p: sum(c.isalpha() for c in p) >= 5,  # Ít nhất 5 ký tự chữ cái
    lambda p: any(c.isdigit() for c in p),  # KHÔNG được thiếu số
    lambda p: sum(1 for c in p if c.isupper()) == 1 and p[len(p) // 2].isupper(),  # Chỉ có 1 chữ cái in hoa và nó nằm ở giữa
    lambda p: 1 <= sum(1 for c in p if c in "!@#$%^&*()_+-=[]{}|;:,.<>?") <= 2,  # Chỉ có 1 hoặc 2 ký tự đặc biệt
    lambda p: sum(int(c) for c in p if c.isdigit()) == 25 if any(c.isdigit() for c in p) else False,  # KHÔNG được có tổng chữ số khác 25
    lambda p: sum(1 for month in ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"] if month in p.lower()) == 1,  # Chỉ có duy nhất 1 tháng
    lambda p: check_roman_numerals(p),  # Số La Mã có thể viết thường hoặc hoa
    lambda p: check_roman_numeral_product(p),  # KHÔNG được có tích số La Mã khác 35
    lambda p: any(element in p for element in ["He", "Li", "Be", "Ne", "Na", "Mg", "Al", "Si", "Cl", "Ar"]),  # KHÔNG được thiếu ký hiệu 2 chữ từ bảng tuần hoàn
    lambda p: check_leap_year(p),  # KHÔNG được thiếu năm nhuận
]

rule_descriptions = [
    "KHÔNG được có ít hơn 5 ký tự chữ cái.",
    "KHÔNG được thiếu ít nhất một chữ số.",
    "KHÔNG được có nhiều hơn hoặc ít hơn một chữ cái in hoa, và nó phải nằm ở giữa.",
    "KHÔNG được có ít hơn một ký tự đặc biệt và không được có quá hai.",
    "KHÔNG được có tổng các chữ số khác 25.",
    "Must NOT contain more than one month of the year.",
    "KHÔNG được thiếu ít nhất một số La Mã (tính cả viết hoa và thường).",
    "KHÔNG được có tích của các số La Mã khác 35.",
    "KHÔNG được thiếu ít nhất một ký hiệu hai chữ cái từ bảng tuần hoàn.",
    "KHÔNG được thiếu ít nhất một năm nhuận.",
]

# Hàm kiểm tra số La Mã (cho phép viết thường)
def check_roman_numerals(password):
    roman_pattern = r'(?i)(ix|iv|viii|vii|vi|iii|ii|i|v|x)'  # Không dùng \b
    return bool(re.search(roman_pattern, password))

# Hàm tính tích số La Mã
def check_roman_numeral_product(password):
    roman_values = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
    roman_pattern = r'(?i)(IX|IV|VIII|VII|VI|III|II|I|V|X)'  # Không dùng \b
    matches = re.findall(roman_pattern, password, re.IGNORECASE)
    
    if not matches:
        return False  # Không có số La Mã nào, không cần kiểm tra
    
    product = 1
    for match in matches:
        product *= roman_values[match.upper()]  # Chuyển về viết hoa để tra bảng giá trị
    
    return product == 35
# Hàm kiểm tra năm nhuận
def check_leap_year(password):
    years = re.findall(r'\d{4}', password)
    for year in years:
        year_int = int(year)
        if (year_int % 4 == 0 and year_int % 100 != 0) or (year_int % 400 == 0):
            return True
    return False

# Lưu trạng thái người chơi
user_progress = {}

async def start(update, context):
    user_id = update.message.from_user.id
    user_progress[user_id] = 0  # Bắt đầu từ quy tắc 0
    await update.message.reply_text("Chào mừng bạn đến với thử thách 5 không! Nhiệm vụ của bạn là tạo ra một mật khẩu đáp ứng tất cả yêu cầu của chúng tôi để có thể nhận được OTT của mật thư. Hãy nhập một mật khẩu để bắt đầu.\nQuy tắc 1: " + rule_descriptions[0])

async def check_password(update, context):
    user_id = update.message.from_user.id
    if user_id not in user_progress:
        await update.message.reply_text("Vui lòng bắt đầu bằng lệnh /start!")
        return

    password = update.message.text.strip()
    current_rule = user_progress[user_id]

    passed_rules = []  # Danh sách quy tắc đã vượt qua

    # Kiểm tra từng quy tắc một
    for i in range(current_rule, len(rules)):
        if rules[i](password):
            passed_rules.append(f"✅ Quy tắc {i + 1}: {rule_descriptions[i]}\n")
        else:
            # Nếu gặp quy tắc đầu tiên bị sai, dừng lại ngay
            await update.message.reply_text(
                "\n".join(passed_rules) +
                f"\n❌ Mật khẩu của bạn vi phạm Quy tắc {i + 1}: {rule_descriptions[i]}"
            )
            return

    # Nếu không bị sai quy tắc nào, cập nhật trạng thái và tiếp tục
    user_progress[user_id] = len(rules)
    await update.message.reply_text("\n".join(passed_rules) + "\n🎉 Chúc mừng! Bạn đã vượt qua tất cả các quy tắc và chiến thắng!\n\nĐây là OTT của mật thư: \nTiếng Chuông vọng mãi trời nam,\nNgười Già như Trẻ chung làm núi sông.\nNgười nằm xuống, đất ôm lòng,\nNgười còn ở lại tiếp dòng ngày mai.")
    del user_progress[user_id]


def main():
    # Token bot của bạn
    TOKEN = "7987710274:AAHcVwXjciqbgbgQBDCZV6K7Dd8EekNIBp0"
    
    # Tạo ứng dụng
    application = Application.builder().token(TOKEN).build()

    # Thêm handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_password))

    # Chạy bot
    application.run_polling()

if __name__ == "__main__":
    main()