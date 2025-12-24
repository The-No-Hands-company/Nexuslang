import sys
try:
    from nlpl.runtime.structures import UnionDefinition
    
    fields = [('i', 'Integer'), ('f', 'Float')]
    ud = UnionDefinition('MyData', fields)
    
    with open('debug_out.txt', 'w') as f:
        f.write(f"Size: {ud.size}\n")
        f.write(f"Alignment: {ud.alignment}\n")
except Exception as e:
    with open('debug_out.txt', 'w') as f:
        f.write(f"Error: {e}\n")
