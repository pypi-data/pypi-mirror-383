from aiogram.filters.callback_data import CallbackData


class NavCallbackData(CallbackData, prefix="nav"):  # navigate menu
    to: str


flags = {
    "RUB": "🇷🇺",
    "THB": "🇹🇭",
    "IDR": "🇮🇩",
    "TRY": "🇹🇷",
    "GEL": "🇬🇪",
    "VND": "🇻🇳",
    "AED": "🇦🇪",
    "AMD": "🇦🇲",
    "AZN": "🇦🇿",
    "CNY": "🇨🇳",
    "EUR": "🇪🇺",
    "HKD": "🇭🇰",
    "INR": "🇮🇳",
    "PHP": "🇵🇭",
    "USD": "🇺🇸",
}
