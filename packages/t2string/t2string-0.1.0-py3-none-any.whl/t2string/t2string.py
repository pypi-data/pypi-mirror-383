from string.templatelib import Template

def t2string(t_string: Template) -> str :
    values: list[str] = []
    
    for i in t_string:
        if isinstance(i, str):
            values.append(i)
        else:
            values.append(i.value)
            
    return "".join(values)