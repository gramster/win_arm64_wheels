from svg_wheel import generate_svg_wheel
from utils import (
    annotate_wheels,
    get_top_packages,
    remove_irrelevant_packages,
    save_to_file,
)

TO_CHART = 5000
css_meaning = {
    'success': 'pure Python',
    'warning': 'native with pure Python fallback',
    'danger': 'native-only, no WinArm64',
    'info': 'cgohlke-provided',
    'primary': 'has WinARM64 wheels',
    'default': 'no wheels',
}


def main():
    packages = remove_irrelevant_packages(get_top_packages(), TO_CHART)
    annotate_wheels(packages)
    count = {}
    for c in set([p['css_class'] for p in packages]):
        count[c] = 0
    for p in packages:
        count[p['css_class']] += 1
    for k in count.keys():
        print(f'{css_meaning[k]}: {count[k]}')
    save_to_file(packages, "results.json")
    generate_svg_wheel(packages, TO_CHART)


if __name__ == "__main__":
    main()
