# XWQuery Console - Quick Reference Card

## 🚀 Getting Started

```bash
cd xwnode/examples/xwnode_console
python run.py
```

---

## 📋 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `.help` | Show help information | `.help` |
| `.collections` | List all collections with counts | `.collections` |
| `.show <name>` | Display sample records from collection | `.show users` |
| `.examples` | Show all example categories | `.examples` |
| `.examples <type>` | Show examples by type | `.examples core` |
| `.random` | Get a random example query | `.random` |
| `.history` | View command history | `.history` |
| `.clear` | Clear the screen | `.clear` |
| `.exit` | Exit the console | `.exit` |

---

## 📊 Example Categories

| Category | Command | Examples |
|----------|---------|----------|
| **Core** | `.examples core` | SELECT, INSERT, UPDATE, DELETE, CREATE, DROP |
| **Filtering** | `.examples filtering` | WHERE, FILTER, LIKE, IN, HAS, BETWEEN, RANGE |
| **Aggregation** | `.examples aggregation` | COUNT, SUM, AVG, MIN, MAX, GROUP BY |
| **Ordering** | `.examples ordering` | ORDER BY |
| **Graph** | `.examples graph` | MATCH, PATH, TRAVERSE |
| **Projection** | `.examples projection` | PROJECT, EXTEND |
| **Advanced** | `.examples advanced` | JOIN, UNION, WINDOW |
| **All** | `.examples all` | Show everything |

---

## 💾 Available Collections

| Collection | Records | Description |
|------------|---------|-------------|
| `users` | 50 | User accounts with profiles |
| `products` | 100 | Product catalog |
| `orders` | 200 | Order transactions |
| `posts` | 30 | Blog posts |
| `events` | 500 | Event logs |

---

## 🔍 Sample Queries

### Basic Selection
```sql
SELECT * FROM users
SELECT name, age FROM users
```

### Filtering
```sql
SELECT * FROM users WHERE age > 30
SELECT * FROM products WHERE price < 50
```

### Aggregation
```sql
SELECT COUNT(*) FROM users
SELECT category, COUNT(*) FROM products GROUP BY category
SELECT AVG(price) FROM products
```

### Ordering
```sql
SELECT * FROM users ORDER BY age
SELECT * FROM products ORDER BY price DESC
```

### Limiting Results
```sql
SELECT * FROM events LIMIT 10
```

---

## 🎯 Quick Tips

1. **Get Help Anytime:** Type `.help` to see available commands
2. **See Examples:** Use `.examples` to learn query syntax
3. **Explore Data:** Use `.show <collection>` to see sample records
4. **Random Inspiration:** Use `.random` for query ideas
5. **Review History:** Use `.history` to see past commands
6. **Exit Safely:** Use `.exit` or press Ctrl+C

---

## 🧪 Testing Commands

```bash
# Run comprehensive test suite
python test_all_operations.py

# Run interactive simulation
python test_interactive.py

# Run full demonstration
python demo.py
```

---

## 📖 Documentation

- **TESTING_COMPLETE.md** - Comprehensive testing documentation
- **CONSOLE_FIX_SUMMARY.md** - Executive summary and fix details
- **QUICK_REFERENCE.md** - This file

---

## ✅ Status

**All Features Working:** ✅  
**Version:** 0.0.1  
**Last Updated:** October 11, 2025

---

**Need More Help?**
- Read `TESTING_COMPLETE.md` for detailed documentation
- Check `../../../CONSOLE_FIX_SUMMARY.md` for fix details
- Run `demo.py` for a full feature demonstration

