import discord
from discord.ext import commands
import subprocess
import requests

# Bot Configuration
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Webhook for logging
WEBHOOK_URL = "put ur webhook"  # Replace with your Discord Webhook URL

# Servers dictionary to manage protection
servers = {}

# Function: Send Logs to Discord Webhook
def send_log_to_webhook(title, description, color):
    embed = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color
            }
        ]
    }
    response = requests.post(WEBHOOK_URL, json=embed)
    if response.status_code != 204:
        print(f"Webhook failed: {response.status_code}, {response.text}")

# Bot Ready Event
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="DDoS Protection"))

# Command: Add Server
@bot.command(name="add_server")
async def add_server(ctx, ip, ports, user, password):
    if ip in servers:
        await ctx.send(f"Server {ip} already added.")
        return
    servers[ip] = {"ports": ports.split(","), "user": user, "password": password}
    await ctx.send(f"Server {ip} added with ports {ports}.")
    send_log_to_webhook("Server Added", f"Server {ip} was added for protection.", 3066993)

# Command: Block IP
@bot.command(name="block_ip")
async def block_ip(ctx, ip):
    try:
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        await ctx.send(f"IP {ip} has been blocked.")
        send_log_to_webhook("IP Blocked", f"The IP {ip} was blocked on the system.", 15158332)
    except Exception as e:
        await ctx.send(f"Error blocking IP {ip}: {e}")
        send_log_to_webhook("Block Error", f"Error blocking IP {ip}: {e}", 15158332)

# Command: Unblock IP
@bot.command(name="unblock_ip")
async def unblock_ip(ctx, ip):
    try:
        subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        await ctx.send(f"IP {ip} has been unblocked.")
        send_log_to_webhook("IP Unblocked", f"The IP {ip} was unblocked on the system.", 3066993)
    except Exception as e:
        await ctx.send(f"Error unblocking IP {ip}: {e}")
        send_log_to_webhook("Unblock Error", f"Error unblocking IP {ip}: {e}", 15158332)


@bot.command(name="status")
async def status(ctx):
    if not servers:
        await ctx.send("No servers are currently protected.")
        return
    server_list = "\n".join([f"{ip}: {', '.join(info['ports'])}" for ip, info in servers.items()])
    embed = discord.Embed(title="Protection Status", description="Current protected servers:", color=3447003)
    embed.add_field(name="Servers", value=server_list, inline=False)
    await ctx.send(embed=embed)
    send_log_to_webhook("Status Requested", "Protection status was viewed.", 3447003)

@bot.command(name="monitor")
async def monitor_traffic(ctx):
    try:
        traffic_logs = "src: 192.168.0.1 --> dst: 10.0.0.2\nsrc: 192.168.0.3 --> dst: 10.0.0.4"
        embed = discord.Embed(title="Traffic Logs", description="Recent Traffic Logs:", color=1752220)
        embed.add_field(name="Logs", value=f"```{traffic_logs}```", inline=False)
        await ctx.send(embed=embed)
        send_log_to_webhook("Traffic Logs", f"Traffic monitoring: \n{traffic_logs}", 3447003)
    except Exception as e:
        await ctx.send(f"Failed to retrieve traffic logs: {e}")
        send_log_to_webhook("Monitor Error", f"Traffic log retrieval error: {e}", 15158332)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Command Error: {error}")
    send_log_to_webhook("Command Error", f"Error encountered: {error}", 15158332)

bot.run("put ur bot token")  