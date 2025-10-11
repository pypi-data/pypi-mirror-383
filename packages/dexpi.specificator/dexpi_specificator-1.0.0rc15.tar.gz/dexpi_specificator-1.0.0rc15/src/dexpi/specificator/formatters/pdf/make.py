import os
import pathlib
import shutil
import subprocess
import unicodedata

from lxml import etree, html
from sphinx.cmd.build import main as sphinx_build_main

from ...sphinx_ext import set_data, SpecificatorData


def make(model_set, config):
    out_dir = pathlib.Path(config['out_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)  
    
    original_sphinx_project_dir = pathlib.Path(config['sphinx_project'])
    if not original_sphinx_project_dir.is_dir():
        raise Exception() # TODO
    try:
        shutil.rmtree(out_dir)
    except FileNotFoundError:
        pass

    sphinx_project_dir = out_dir / '.sphinx'
    shutil.copytree(original_sphinx_project_dir, sphinx_project_dir)

    (sphinx_project_dir / 'images').mkdir(parents=True, exist_ok=False)
    for path, index in config['index_by_path'].items():
        
        assert path.endswith('.svg')
        path = pathlib.Path(path[:-4] + '.pdf')
        if not path.is_file():
            print("WARN", path)
            
            continue
        shutil.copy(path, sphinx_project_dir / 'images' / f'img{index}.pdf')

    model_dir = sphinx_project_dir / '_models'
    model_dir.mkdir(parents=True)

    data = SpecificatorData(
        model_set=model_set,
        config=config)

    with set_data(data):
        sphinx_build_main(['-M',
            'latex',
            str(sphinx_project_dir),
            str(out_dir),
            '-v'])
        
    clean_latex(out_dir)
    
    tex_path = out_dir / 'latex' / 'dexpispecification.tex'
    
    for _ in range(4):
        subprocess.check_call(
            ['pdflatex',
             'dexpispecification.tex'],
            cwd=out_dir / 'latex')

        
        
        
    os.rename(
        out_dir / 'latex' / 'dexpispecification.pdf',
        out_dir / 'DEXPI Specification 2.0.0.pdf')
        

    
def clean_latex(out_dir):

    tex_path = out_dir / 'latex' / 'dexpispecification.tex'
    tex_code = tex_path.read_text(encoding='utf-8') # TODO encoding)
    
    for old, new in [
            (unicodedata.lookup('DOT OPERATOR'), r'$\cdotp$'),
            (unicodedata.lookup('BULLET OPERATOR'), r'$\cdotp$'),
            (unicodedata.lookup('GREEK CAPITAL LETTER THETA'), r'$\Theta$'),
            (r'⁻\(\sp{\text{1}}\)', '$^{-1}$')]:
        tex_code = tex_code.replace(old, new)
    
    lines = []
    for line in tex_code.splitlines(keepends=True):

        use_sphinx_messages = r'\usepackage{sphinxmessages}'
        if line.startswith(use_sphinx_messages):
            line = r'\usepackage{tikz}\usetikzlibrary{arrows,arrows.meta}\usepackage[export]{adjustbox}' + line

        # replace sphinxincludegraphics with input of tex TikZ files.
        sphinx_include = r'\noindent\sphinxincludegraphics{{uml-'
        if line.startswith(sphinx_include):
            line = r'\noindent\adjustbox{max width=\linewidth}{\input{{uml-' + line[len(sphinx_include):] + '}'

        lines.append(line)

    tex_path.write_text(''.join(lines), encoding='utf-8') # TODO encoding?

