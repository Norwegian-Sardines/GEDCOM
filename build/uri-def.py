import re
from sys import argv, stderr
from os.path import isfile, isdir, exists, dirname, join
from os import makedirs
from subprocess import run


def get_paths():
    """Parses command-line arguments, if present; else uses defaults"""
    spec = join(dirname(argv[0]),'../specification/gedcom.md') if len(argv) < 2 or not isfile(argv[1]) else argv[1]
    dest = join(dirname(argv[0]),'../extracted-files/tags')
    for arg in argv:
        if arg and isdir(arg):
            dest = arg
            break
        if arg and not exists(arg) and arg[0] != '-' and isdir(dirname(arg)):
            dest = arg
            break

    if not isdir(dest):
        makedirs(dest)
    
    return spec, dest

def get_text(spec):
    """Reads the contents of the given file"""
    with open(spec) as fh: return fh.read()

def get_prefixes(txt):
    """Find and parse prefix definition tables"""
    pfx = {}
    for pfxtable in re.finditer(r'([^\n]*)Short Prefix *\| *URI Prefix *\|(\s*\|[^\n]*)*', txt):
        for abbr, lng in re.findall(r'`([^`]*)` *\| *`([^`]*)`', pfxtable.group(0)):
            pfx[abbr] = lng
    return pfx

def find_datatypes(txt, g7):
    """Returns datatype:uri and adds URI suffixes to g7"""
    dturi = {}
    for section in re.finditer(r'^#+ *([^\n]*)\n+((?:[^\n]|\n+[^\n#])*[^\n]*URI for[^\n]*datatypes? is(?:[^\n]|\n+[^\n#])*)', txt, re.M):
        for dt, uri in re.findall(r'URI[^\n]*`([^\n`]*)` datatype[^\n]*`([^`\n:]*:[^\n`]*)`', section.group(0)):
            dturi[dt] = uri
            if uri.startswith('g7:'):
                if '#' in uri: uri = uri[:uri.find('#')]
                if uri[3:] not in g7:
                    g7[uri[3:]] = ('datatype', [section.group(2).strip()])
    return dturi
    
def find_cat_tables(txt, g7, tagsets):
    """Looks for tables of tags preceded by a concatenation-based URI
    
    Raises an exception if any URI is repeated with distinct definitions. This code contains a hard-coded fix for BIRTH which has the same unifying concept but distinct text in the spec.
    
    Returns a {structure:[list,of,allowed,enums]} mapping
    """
    hard_code = {
        "g7:enum-BIRTH": 'Associated with birth, such as a birth name or birth parents.',
    }
    cats = {}
    enums = {}
    for bit in re.finditer(r'by\s+concatenating\s+`([^`]*)`', txt):
        i = txt.rfind('\n#', 0, bit.start())
        j = txt.find(' ',i)
        j = txt.find(txt[i:j+1], j)
        sect = txt[i:j].replace('(Latter-Day Saint Ordinance)','`ord`') ## <- hack for ord-STAT
        for entry in re.finditer(r'`([A-Z0-9_]+)` *\| *(.*?) *[|\n]', sect):
            enum, meaning = entry.groups()
            pfx = bit.group(1)+enum
            if 'The URI of this' in meaning:
                meaning, tail = meaning.split('The URI of this')
                pfx = tail.split('`')[1]
            meaning = hard_code.get(pfx,meaning)
            if pfx in cats and meaning != cats[pfx]:
                raise Exception('Concatenated URI '+pfx+' has multiple definitions:'
                    + '\n    '+cats[pfx]
                    + '\n    '+meaning
                )
            if 'enum-' in pfx:
                k1 = sect.find('`', sect.rfind('\n#', 0, entry.start()))
                k2 = sect.rfind('`', 0, sect.find('\n', k1))
                key = sect[k1:k2].replace('`','').replace('.','-')
                enums.setdefault(key,[]).append(pfx)
            if pfx not in cats:
                cats[pfx] = meaning
                if pfx.startswith('g7:'):
                    if pfx[3:] in g7:
                        raise Exception(pfx+' defined as an enumeration and a '+g7[pfx[3:]][0])
                    g7[pfx[3:]] = ('enumeration', [meaning])
    return enums

def find_calendars(txt, g7):
    """Looks for sections defining a `g7:cal-` URI"""
    for bit in re.finditer(r'#+ `[^`]*`[^\n]*\n+((?:\n+(?!#)|[^\n])*is `g7:(cal-[^`]*)`(?:\n+(?!#)|[^\n#])*)', txt):
        g7[bit.group(2)] = ('calendar',[bit.group(1)])
        

def joint_card(c1,c2):
    """Given two cardinalities, combine them."""
    return '{' + ('1' if c1[1] == c2[1] == '1' else '0') + ':' + ('1' if c1[3] == c2[3] == '1' else 'M') + '}'

def parse_rules(txt):
    """returns {rule:[(card,uri),(card,uir),...] for each level-n
    production of the rule, even if indirect (via another rule),
    regardless of if alternation or set."""
    # Find gedstruct context
    rule_becomes = {}
    rule_becomes_rule = {}
    for rule,block,notes in re.findall(r'# *`([A-Z_0-9]+)` *:=\s+```+[^\n]*\n([^`]*)``+[^\n]+((?:[^\n]|\n(?!#))*)', txt):
        for card, uri in re.findall(r'^n [A-Z@][^\n]*(\{.:.\}) *(\S+:\S+)', block, re.M):
            rule_becomes.setdefault(rule,[]).append((card, uri))
        for r2, card in re.findall(r'^n <<([^>]*)>>[^\n]*(\{.:.\})', block, re.M):
            rule_becomes_rule.setdefault(rule,[]).append((card, r2))
    # Fixed-point rule-to-rule resolution
    again = True
    while again:
        again = False
        for r1,rset in tuple(rule_becomes_rule.items()):
            flat = True
            for c,r2 in rset:
                if r2 in rule_becomes_rule:
                    flat = False
            if flat:
                for c,r2 in rset:
                    rule_becomes.setdefault(r1,[]).extend((joint_card(c,c2),uri) for (c2,uri) in rule_becomes[r2])
                del rule_becomes_rule[r1]
            else:
                again = True
    return rule_becomes

def new_key(val, d, *keys, msg=''):
    """Helper method to add to a (nested) dict and raise if present"""
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    if keys[-1] in d:
        if d[keys[-1]] != val:
            raise Exception(msg+'Duplicate key: '+str(keys))
    else: d[keys[-1]] = val

def parse_gedstruct(txt, rules, dtypes):
    """Reads through all gedstruct blocks to find payloads, substructures, and superstructures"""
    sup,sub,payload = {}, {}, {}
    for block in re.findall(r'```[^\n]*gedstruct[^\n]*\n([^`]*)\n```', txt):
        stack = []
        for line in block.split('\n'):
            parts = line.strip().split()
            if len(parts) < 3:
                if line not in ('[','|',']'):
                    raise Exception('Invalid gedstruct line: '+repr(line))
                continue
            if parts[1].startswith('@'): del parts[1]
            if parts[0] == 'n': stack = []
            else:
                n = int(parts[0])
                while n < len(stack): stack.pop()
            if parts[1].startswith('<'):
                card = parts[2]
                if len(stack):
                    for c,u in rules[parts[1][2:-2]]:
                        new_key(joint_card(card,c), sup, u, stack[-1], msg='rule sup: ')
                        new_key(joint_card(card,c), sub, stack[-1], u, msg='rule sub: ')
            else:
                uri = parts[-1]
                if '{' in uri:
                    uri = parts[1]+' pseudostructure'
                card = parts[-2]
                if len(parts) > 4:
                    p = ' '.join(parts[2:-2])[1:-1]
                    if p.startswith('<XREF:'): p = '@'+p+'@'
                    elif p == 'Y|<NULL>': pass
                    else: p = dtypes[p]
                else: p = None
                new_key(p, payload, uri, msg='payload: ')
                if len(stack):
                    new_key(card, sup, uri, stack[-1], msg='line sup: ')
                    new_key(card, sub, stack[-1], uri, msg='line sub: ')
                stack.append(uri)
    return {k:{'sub':sub.get(k,[]),'sup':sup.get(k,[]),'pay':payload.get(k)} for k in sub.keys()|sup.keys()|payload.keys()}

def find_descriptions(txt, g7, ssp):
    """Collects structure definitions as follows:
    
    - Sections '#+ TAG (Name) `g7:FULL.TAG`'
    - Sections '#+ `RULE` :=' with only one level-n struct
    - Rows in tables 'Tag | Name<br/>URI | Description'
    
    Returns a {section header:[list,of,uris]} mapping
    """
    
    # structure sections
    for name,uri,desc in re.findall(r'#+ `[^`]*`[^\n]*\(([^)]*)\)[^\n]*`([^:`\n]*:[^`\n]*)`[^\n]*\n+((?:\n+(?!#)|[^\n])*)', txt):
        if uri not in ssp:
            raise Exception('Found section for '+uri+' but no gedstruct')
        if uri.startswith('g7:'):
            g7.setdefault(uri[3:],('structure',[],ssp[uri]))[1].extend((
                name.strip(),
                desc.strip()
            ))
            for other in re.findall(r'[Aa] type of `(\S*)`', desc):
                m = re.search('^#+ +`'+other+r'`[^\n`]*\n((?:[^\n]+|\n+(?!#))*)', txt, re.M)
                if m:
                    g7[uri[3:]][1].append(m.group(1).strip())
    
    # error check that gedstruct and sections align
    for uri in ssp:
        if 'pseudostructure' in uri: continue
        if uri.startswith('g7:') and uri[3:] not in g7:
            raise Exception('Found gedstruct for '+uri+' but no section')

    # gedstruct sections
    for uri, desc in re.findall(r'#+ *`[^`]*` *:=[^\n]*\n+`+[^\n]*\n+n [^\n]*\} *(\S+:\S+) *(?:\n [^\n]*)*\n`+[^\n]*\n+((?:[^\n]|\n(?!#))*)', txt):
        g7[uri[3:]][1].append(desc.strip())
    
    tagsets = {}
    # tag tables
    for table in re.finditer(r'\n#+ (\S[-A-Za-z0-9 ]*[a-z0-9])[^#]*?Tag *\| *Name[^|\n]*\| *Description[^\n]*((?:\n[^\n|]*\|[^\n|]*\|[^\n]*)*)', txt):
        pfx = ''
        header = table.group(1)
        if header.startswith('Fam'): pfx = 'FAM-'
        if header.startswith('Indi'): pfx = 'INDI-'
        for tag, name, desc in re.findall(r'`([A-Z_0-9]+)` *\| *([^|\n]*?) *\| *([^|\n]*[^ |\n]) *', table.group(2)):
            if '<br' in name: name = name[:name.find('<br')]
            if tag not in g7: tag = pfx+tag
            if tag not in g7:
                raise Exception('Found table for '+tag+' but no section or structure')
            if g7[tag][0] != 'structure':
                raise Exception('Found table for '+tag+' but that\'s a '+g7[tag][0]+' not a structure')
            tagsets.setdefault(header,[]).append(tag)
            g7[tag][1].append(name.strip())
            g7[tag][1].append(desc.strip())
    return tagsets

def find_enum_by_link(txt, enums, tagsets):
    """Extend enums with the tagsets suggested by any section with #enum- in the header that lacks a table and links to Events or Attributes"""
    for sect in re.finditer(r'# *`([A-Z0-9_`.]*)`[^\n]*#enum-[\s\S]*?\n#', txt):
        if '[Events]' in sect.group(0):
            key = sect.group(1).replace('`','').replace('.','-')
            for k in tagsets:
                if 'Event' in k:
                    enums.setdefault(key, []).extend('g7:'+_ for _ in tagsets[k])
        if '[Attributes]' in sect.group(0):
            key = sect.group(1).replace('`','').replace('.','-')
            for k in tagsets:
                if 'Attribute' in k:
                    enums.setdefault(key, []).extend('g7:'+_ for _ in tagsets[k])

def tidy_markdown(md, indent, width=79):
    """Run markdown through pandoc to remove markup and wrap columns"""
    global prefixes
    for k,v in prefixes.items():
        md = re.sub(r'\b'+k+':', v, md)
    out = run(['pandoc','-t','plain','--columns='+str(width-indent)], input=md.encode('utf-8'), capture_output=True)
    return out.stdout.rstrip().decode('utf-8').replace('\n','\n'+' '*indent)

def yaml_str_helper(pfx, md, width=79):
    txt = tidy_markdown(md, len(pfx), width)
    if ('\n'+' '*len(pfx)+'\n') in txt: return pfx + '|\n' + ' '*len(pfx) + txt
    return pfx + txt

def expand_prefix(txt, prefixes):
    for key in sorted(prefixes.keys(), key=lambda x:-len(x)):
        k = key+':'
        if txt.startswith(k):
            return prefixes[key] + txt[len(k):]
    return txt

if __name__ == '__main__':
    # URI definitions
    g7 = {}
    spec, dest = get_paths()
    txt = get_text(spec)
    
    prefixes = get_prefixes(txt)
    dtypes = find_datatypes(txt, g7)
    rules = parse_rules(txt)
    ssp = parse_gedstruct(txt, rules, dtypes)
    tagsets = find_descriptions(txt, g7, ssp)
    enums = find_cat_tables(txt, g7, tagsets)
    find_enum_by_link(txt, enums, tagsets)
    find_calendars(txt, g7)

    struct_lookup = []
    enum_lookup = []
    payload_lookup = []
    cardinality_lookup = []

    for tag in g7:
        print('outputting', tag, '...', end=' ')
        with open(join(dest,tag), 'w') as fh:
            fh.write('%YAML 1.2\n---\n')
            print('type:',g7[tag][0], file=fh)
            
            # error: type-DATE# type-List#
            uri = expand_prefix('g7:'+tag,prefixes)
            print('\nuri:', uri, file=fh)
            
            if g7[tag][0] in ('structure', 'enumeration', 'calendar', 'month'):
                ptag = re.sub(r'.*-', '', tag)
                print('\nstandard tag: '+ptag, file=fh)
            
            print('\ndescriptions:', file=fh)
            for desc in g7[tag][1]:
                print(yaml_str_helper('  - ', desc), file=fh)
            if g7[tag][0] == 'structure':
                d = g7[tag][2]
                payload = expand_prefix(d['pay'],prefixes) if d['pay'] is not None else 'null'
                print('\npayload:', payload, file=fh)
                payload_lookup.append([uri, payload if payload != 'null' else ''])
                if d['pay'] and 'Enum' in d['pay']:
                    print('\nenumeration values:', file=fh)
                    for k in sorted(enums[tag]):
                        penum = re.sub(r'.*[-:/]', '', k)
                        puri = expand_prefix(k,prefixes)
                        print('  '+penum+':', expand_prefix(k,prefixes), file=fh)
                        enum_lookup.append([uri,penum,puri])
                if d['sub']:
                    print('\nsubstructures:', file=fh)
                    for k,v in sorted(d['sub'].items()):
                        print('  "'+expand_prefix(k,prefixes)+'": "'+v+'"', file=fh)
                else: print('\nsubstructures: []', file=fh)
                if d['sup']:
                    print('\nsuperstructures:', file=fh)
                    for k,v in sorted(d['sup'].items()):
                        suri = expand_prefix(k,prefixes)
                        print('  "'+suri+'": "'+v+'"', file=fh)
                        struct_lookup.append([suri,ptag,uri])
                        cardinality_lookup.append([suri,uri,v])
                else:
                    print('\nsuperstructures: []', file=fh)
                    struct_lookup.append(['',ptag,uri])
            fh.write('...\n')

        print('done')

    if dest.endswith('/'): dest=dest[:-1]
    base = dirname(dest)
    for data,name in [
        (struct_lookup, join(base,'substructures.tsv')),
        (enum_lookup, join(base,'enumerations.tsv')),
        (payload_lookup, join(base,'payloads.tsv')),
        (cardinality_lookup, join(base,'cardinalities.tsv')),
    ]:
        print('outputting', name, '...', end=' ')
        with open(name, 'w') as f:
            for row in data:
                print('\t'.join(row), file=f)
        print('done')
