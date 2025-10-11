import os
import pathlib
import shutil

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
        shutil.copy(path, sphinx_project_dir / 'images' / f'img{index}.svg')

    model_dir = sphinx_project_dir / '_models'
    model_dir.mkdir(parents=True)

    data = SpecificatorData(
        model_set=model_set,
        config=config)

    with set_data(data):
        sphinx_build_main(['-M',
            'html',
            str(sphinx_project_dir),
            str(out_dir),
            '-v'])
        
    xml_dir = out_dir.parent / 'xml'
    assert xml_dir.is_dir()
    if len(list(xml_dir.iterdir())) == 4:
    
        for p in xml_dir.iterdir():
            content = p.read_bytes()
            (out_dir / 'html' / '_static' / p.name).write_bytes(content)
    
            
    clean_html(out_dir)
    
    
    

            
    
def clean_html(out_dir):
    
    print('cleaning HTML...')
    
    for html_path in out_dir.glob('**/*.html'):
        html_tree = html.parse(html_path)
        
        changed = False
        
        for img in html_tree.xpath('//img'):
            # TODO: clean link conversion
            rel_src = img.attrib.get('src')
            if '_images/uml' not in rel_src:
                continue
            changed = True
            abs_src = (html_path.parent / rel_src).resolve()
            assert abs_src.is_file()
            svg_element = etree.parse(abs_src).getroot()

            # Remove SVG namespace.
            for element in svg_element.iter():
                element.tag = element.tag[28:]
            
            del svg_element.attrib['height']
            assert 'style' not in svg_element.attrib
            svg_element.attrib['style'] = 'max-width: 100%; background-color: white;'
            
            for a_element in svg_element.iter('a'):
                href = a_element.attrib['href']
                new_href = str((abs_src.parent / href).relative_to(html_path.parent, walk_up=True)).replace(os.sep, '/')
                new_href = new_href.replace('/_images/../', '/')
                a_element.attrib['href'] = new_href

            img.getparent().replace(img, svg_element)
                
                
           

            
        for admonition_p in html_tree.xpath("//p[@class='admonition-title']"):
            if admonition_p.text:
                admonition_p.text = admonition_p.text.title()
                changed = True

        if changed:
            html_code = etree.tostring(
                html_tree,
                method='html',
                encoding='utf-8')
            
            assert b'<a id="mode_toggle" href="#" :title="mode">' in html_code
            html_code = html_code.replace(
                b'<a id="mode_toggle" href="#" :title="mode">',
                b'<a id="mode_toggle" href="#" @click.prevent="handleClick" :title="mode">')

            html_path.write_bytes(html_code)
            
    print('done')

            
            
            
            
            
            
            
            
            
            
            
