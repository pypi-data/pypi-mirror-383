# 🛡️ Cybuddy 

**Your cybersecurity learning companion** — Get instant answers about security tools, attack techniques, and CTF scenarios. No tabs, no confusion, just fast learning.

## Access Levels
Public Access (Free): Everyone can use Cybuddy’s core features and explore hundreds of cybersecurity topics instantly.

**Cyguides Bootcamp Access (Pro)**: Bootcamp users unlock advanced AI-powered prompts, personalized learning paths, and deeper interactive guidance directly integrated within Cybuddy.


## What is Cybuddy?

Cybuddy is an intelligent terminal tool that helps you learn cybersecurity. Instead of juggling 50+ browser tabs and outdated blog posts, you get instant, focused answers through smart commands with intelligent suggestions and learning analytics.

**Built for:** Students learning cyber security • CTF players • Lab learners (HTB, TryHackMe) • Anyone who needs quick security answers


## Why Use Cybuddy?

- **No browser needed** — Everything works in your terminal
- **300+ cybersecurity entries** — Tools, techniques, attack scenarios explained simply  
- **7 focused commands** — Everything you need, nothing you don't
- **Smart suggestions** — Get intelligent recommendations based on your learning history
- **Command analytics** — Track your progress and identify learning patterns
- **Zero configuration** — Works out of the box, no setup required
- **Offline-first** — Built-in knowledge base works without internet
- **Safe defaults** — Won't suggest dangerous commands without warnings

## How to Use

### Quick Start

```bash
# Install
pip install cybuddy

# Start learning
cybuddy
```

That's it. You're ready to learn cybersecurity.

### The 8 Commands

Once you run `cybuddy`, you have exactly 8 commands with smart features:

| Command | Purpose | Example | Smart Features |
|---------|---------|---------|----------------|
| **explain** | Learn what commands/tools do | `explain 'nmap -sV'` | Auto-suggestions for common tools |
| **tip** | Quick study guide for topics | `tip 'SQL injection'` | Context-aware technique suggestions |
| **help** | Troubleshoot errors | `help 'connection refused'` | Smart error pattern matching |
| **report** | Practice writing security reports | `report 'Found SQLi in login'` | Template suggestions based on findings |
| **quiz** | Test your knowledge with flashcards | `quiz 'Buffer Overflow'` | Adaptive difficulty based on history |
| **plan** | Get unstuck with next steps | `plan 'found port 80 open'` | Contextual next-step recommendations |
| **history** | Show your command history | `history` | **NEW**: Analytics, search, smart suggestions |
| **clear** | Clear the terminal screen | `clear` | - |
| **exit** | Leave the interactive mode | `exit` | - |

### Example Usage

```bash
❯ cybuddy

❯ explain 'nmap -sV'
─── Explanation ─────────────────────────────────────
  Network Mapper - powerful port scanner and service detection tool
  -sV: Version detection: probe open ports to determine service/version info
  Use when: Network reconnaissance, port scanning, service enumeration
  ⚠ Use responsibly. Some scans may be detected by IDS/IPS
─────────────────────────────────────────────────────

❯ tip 'SQL injection'
─── Tip ─────────────────────────────────────────────
  • Look for ' or " in inputs to trigger SQL errors
  • Test with: ' OR '1'='1 -- (boolean bypass)
  • Use UNION SELECT to extract data: ' UNION SELECT null,username,password FROM users--
  • Check INFORMATION_SCHEMA for table/column names
  • Always test login pages, search boxes, and URL parameters
─────────────────────────────────────────────────────

❯ plan 'found port 80 open'
─── Next Steps ──────────────────────────────────────
  1. Enumerate web service with nikto -h http://target or whatweb http://target
  2. Check robots.txt, sitemap.xml, and common endpoints (/admin, /api, /.git)
  3. Run directory brute-force with gobuster or ffuf using medium wordlist
─────────────────────────────────────────────────────

❯ history --stats
📊 Command History Analytics:
========================================

📈 Commands by Category:
  explain     :  15
  tip         :   8
  help        :   5
  plan        :   3

🛠️  Most Used Tools/Techniques:
  nmap               :   8
  sql injection      :   5
  burp suite         :   3
  metasploit         :   2

🔥 Recent Patterns (7 days):
  • Network scanning with nmap
  • Web application testing techniques
  • SQL injection exploitation
─────────────────────────────────────────────────────
```


## FAQ

**Q: Is this better than using real security tools?**
No. Cybuddy is a *learning tool* to help you understand and use real tools effectively.

**Q: Does it replace Google/Stack Overflow?**
For quick hints and common tasks, yes. For deep technical dives, no.

**Q: Can I use this during exams/CTFs?**
Check your specific rules. Built-in knowledge base is usually OK.

**Q: Is my data sent anywhere?**
No. Everything is local and offline. Your command history is stored locally in `~/.cybuddy/history.json`.

**Q: How does the smart history work?**
Cybuddy analyzes your command patterns, categorizes your learning topics, and provides intelligent suggestions based on your usage patterns and cybersecurity knowledge base.

**Q: Why is it called Cybuddy?**
It's your cybersecurity buddy — always ready to help you learn, no judgment, no confusion.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Built by learners, for learners.** Someone who remembers being stuck at 2am during a CTF wanted to make learning easier.

## License

MIT License - see LICENSE file for details.

---

**Start learning now:**
```bash
pip install cybuddy
cybuddy
```
