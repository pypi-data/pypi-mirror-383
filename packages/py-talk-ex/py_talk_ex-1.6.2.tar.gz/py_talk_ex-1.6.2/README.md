# Pytalk

py-talk is a simple but powerful pythonic library for making bots for the [TeamTalk5 Conferencing System](https://bearware.dk/)


### Installing

Python 3.8 or higher is required

#### From PyPI

```bash
pip install py-talk-ex
```

#### From source

```bash
git clone https://github.com/BlindMaster24/pytalk
cd pytalk
uv sync
```


### Usage

```python
import teamtalk

bot = pytalk.TeamTalkBot()

@bot.event
async def on_ready():
    test_server = pytalk.TeamTalkServerInfo("localhost", 10335, 10335, "user", "pass")
    await bot.add_server(test_server)

@bot.event
async def on_message(message):
    if message.content.lower() == "ping":
        message.reply("pong")

bot.run()
```


## Documentation

You can find the full documentation [here](http://pytalk.readthedocs.io/en/latest)



## Troubleshooting

#### Erro when downloading the teamtalk sdk


```
Error: patoolib.util.PatoolError: could not find an executable program to extract format 7z; candidates are (7z,7za,7zr,unar),
```

Solution:

```
$ sudo apt install p7zip-full
```

Explanation:

The error is caused by the fact that the `patool` library requires a program to extract 7z files. The error message lists the programs it tried to use, and the solution is to install one of them. In this case, `p7zip-full` is a good choice.


## Contributing

So you want to contribute to teamtalk.py? Great! There are many ways to contribute to this project, and all contributions are welcome.
If you have found a bug, have a feature request or want to help improve documentation please [open an issue](https://github.com/BlindMaster24/pytalk/issues/new)_

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
