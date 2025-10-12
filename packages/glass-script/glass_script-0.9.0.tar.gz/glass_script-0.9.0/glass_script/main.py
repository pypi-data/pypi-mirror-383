# GlassScript
# A structured markup language.
# By splot.dev
# -----------
# Syntax
# Preload:
# (.link)(<a href="{url}">{}</a>)
# User Must Enter:
# (?url)(https://example.com)
# (!link)(Click here!)
# -----------
# "See through the code."

class GlassScript:
    def glass2html(self, code):
        try:
            import re
            from bs4 import BeautifulSoup
            
            escape_char = "^"
            
            if not isinstance(code, str):
                raise ValueError("Must provide string.")
            
            splitcode = code.splitlines()
            parts = []

            for line in splitcode:
                oldparts = re.split(rf'(?<!{re.escape(escape_char)})[()]', line)
                newparts = []
                for oldop in oldparts:
                    if not (oldop == ''):
                        newop = re.sub(rf'{re.escape(escape_char)}([()])', r'\1', oldop)
                        newparts.append(newop)

                if not (newparts == []):
                    parts.append(newparts)

            html = ""

            preloads = {}
            memory = {}

            latter = False
            state = None
            name = None
            value = None
            
            for line in parts:
                try:
                    for command in line:
                        if command.startswith("."):
                            if latter == False:
                                latter = True
                                state = "."
                                name = command[1:]
                        elif command.startswith("?"):
                            if latter == False:
                                latter = True
                                state = "?"
                                name = command[1:]
                        elif command.startswith("!"):
                            if latter == False:
                                latter = True
                                state = "!"
                                name = command[1:]
                        else:
                            if latter == True:
                                latter = False
                                value = command

                                if state == ".":
                                    preloads[name] = value
                                elif state == "?":
                                    memory[name] = value
                                elif state == "!":
                                    if name == "clear":
                                        memory = {}
                                    else:
                                        extract = preloads.get(name, "")
                                        
                                        for nam, val in memory.items():
                                            extract = extract.replace(f"{{{nam}}}", val)
                                            
                                        extract = extract.replace("{}", value)
                                        html = html + extract
                                        
                                latter = False
                                state = None
                                name = None
                                value = None
                except:
                    pass
            soup = BeautifulSoup(html, 'html.parser')
            full_doc = BeautifulSoup('<!DOCTYPE html><html><head></head><body></body></html>', 'html.parser')
            for element in soup:
                if element.name in ["meta", "title", "script", "base"]:
                    full_doc.head.append(element)
                else:
                    full_doc.body.append(element)
            return full_doc.prettify()
        except Exception as e:
            raise SyntaxError(f"Code is likely invalid: {e}")
