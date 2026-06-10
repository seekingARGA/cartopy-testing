from config import *
from logic import *
import discord
import os
import tempfile
from discord.ext import commands
from config import TOKEN

# Menginisiasi pengelola database
manager = DB_Map("database.db")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot started")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Halo, {ctx.author.name}. Masukkan !help_me untuk mengeksplorasi daftar perintah yang tersedia")

@bot.command()
async def help_me(ctx: commands.Context):
    await ctx.send(
        "Berikut adalah daftar perintah yang tersedia:\n"
        "!start - Memulai interaksi dengan bot\n"
        "!help_me - Menampilkan daftar perintah yang tersedia\n"
        "!show_city <nama_kota> - Menampilkan peta dengan kota yang ditentukan\n"
        "!show_my_cities - Menampilkan peta dengan kota-kota yang telah disimpan oleh pengguna\n"
        "!remember_city <nama_kota> - Menyimpan kota ke dalam memori pengguna (gunakan nama kota dalam bahasa Inggris)\n"
        "!change_marker_color <warna> - Mengubah warna penanda kota (red, blue, green, yellow, cyan, magenta, orange, purple, black, gray, brown, pink)"
    )
    
    
        # Implementasi perintah yang akan menampilkan daftar perintah yang tersedia)

@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    if not city_name or not city_name.strip():
        await ctx.send("Gunakan perintah: !show_city <nama_kota>")
        return

    coordinates = manager.get_coordinates(city_name)
    if not coordinates:
        await ctx.send(f"Kota '{city_name}' tidak ditemukan dalam database.")
        return

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        image_path = tmp_file.name

    try:
        user_color = manager.get_user_color(ctx.author.id)
        manager.create_graph(image_path, [city_name], marker_color=user_color)
        await ctx.send(file=discord.File(image_path))
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)  # Mengambil daftar kota yang diingat oleh pengguna
    if not cities:
        await ctx.send("Anda belum menyimpan kota apa pun. Gunakan !remember_city <nama_kota> terlebih dahulu.")
        return

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        image_path = tmp_file.name

    try:
        user_color = manager.get_user_color(ctx.author.id)
        manager.create_graph(image_path, cities, marker_color=user_color)
        await ctx.send(file=discord.File(image_path))
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):  # Memeriksa apakah kota ada dalam database; jika ya, menambahkannya ke memori pengguna
        await ctx.send(f'Kota {city_name} telah berhasil disimpan!')
    else:
        await ctx.send("Format tidak benar. Silakan masukkan nama kota dalam bahasa Inggris, dengan spasi setelah perintah.")


@bot.command()
async def change_marker_color(ctx: commands.Context, color: str):
    # Warna-warna dasar yang tersedia
    basic_colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'orange', 'purple', 'black', 'gray', 'brown', 'pink']
    
    color_lower = color.lower()
    if color_lower not in basic_colors:
        await ctx.send(f"Warna '{color}' tidak valid. Pilih dari: {', '.join(basic_colors)}")
        return
    
    manager.set_user_color(ctx.author.id, color_lower)
    await ctx.send(f"Warna marker telah diubah menjadi **{color_lower}**! Gunakan !show_city atau !show_my_cities untuk melihat perubahan.")

if __name__ == "__main__":
    bot.run(TOKEN)
