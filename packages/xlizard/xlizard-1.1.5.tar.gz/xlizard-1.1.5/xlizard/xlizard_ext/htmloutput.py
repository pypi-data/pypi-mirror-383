from __future__ import print_function
import sys
import os
import datetime
from xlizard.combined_metrics import CombinedMetrics
from xlizard.sourcemonitor_metrics import SourceMonitorMetrics, Config
from xlizard.sourcemonitor_metrics import FileAnalyzer, Config

def html_output(result, options, *_):
    try:
        from jinja2 import Template
    except ImportError:
        sys.stderr.write(
                "HTML Output depends on jinja2. `pip install jinja2` first")
        sys.exit(2)

    # Get SourceMonitor metrics
    try:
        sm = SourceMonitorMetrics(options.paths[0] if options.paths else '.')
        sm.analyze_directory()
        
        # Create metrics dictionary with normalized paths
        sm_metrics = {}
        for m in sm.get_metrics():
            original_path = m['file_path']
            normalized_path = os.path.normpath(original_path)
            basename = os.path.basename(normalized_path)
            
            sm_metrics[normalized_path] = m
            sm_metrics[basename] = m
            sm_metrics[f"./{normalized_path}"] = m
            sm_metrics[normalized_path.replace('\\', '/')] = m
            
    except Exception as e:
        sys.stderr.write(f"Warning: SourceMonitor metrics not available ({str(e)})\n")
        sm_metrics = {}

    file_list = []
    for source_file in result:
        if source_file and not source_file.filename.endswith('.h'):
            file_key = os.path.normpath(source_file.filename)
            file_metrics = sm_metrics.get(file_key) or sm_metrics.get(os.path.basename(file_key))

            combined = CombinedMetrics(
                source_file,
                file_metrics
            )
            
            dirname = combined.dirname
            source_file_dict = {
                "filename": combined.filename,
                "basename": combined.basename,
                "dirname": dirname,
                "comment_percentage": combined.comment_percentage,
                "max_block_depth": combined.max_block_depth,
                "pointer_operations": combined.pointer_operations,
                "preprocessor_directives": combined.preprocessor_directives,
                "logical_operators": combined.logical_operators,
                "conditional_statements": combined.conditional_statements,
                "lines_of_code": combined.lines_of_code,
                "comment_lines": combined.comment_lines,
                "total_lines": combined.total_lines,
                "sourcemonitor": file_metrics
            }
            
            func_list = []
            max_complexity = 0
            for source_function in combined.functions:
                if source_function:
                    func_dict = _create_dict(source_function, source_file.filename)
                    func_dict['in_disable_block'] = _is_in_disable_block(
                        source_file.filename, 
                        source_function.start_line, 
                        source_function.end_line
                    )
                    if not hasattr(source_function, 'token_count'):
                        func_dict['token_count'] = 0
                    func_list.append(func_dict)
                    # Calculate max complexity for the file (only for active functions)
                    if not func_dict['in_disable_block'] and func_dict['cyclomatic_complexity'] > max_complexity:
                        max_complexity = func_dict['cyclomatic_complexity']
            
            source_file_dict["functions"] = func_list
            source_file_dict["max_complexity"] = max_complexity
            
            # Calculate average complexity only for active functions
            active_functions = [f for f in func_list if not f['in_disable_block']]
            source_file_dict["avg_complexity"] = sum(
                func['cyclomatic_complexity'] for func in active_functions
            ) / len(active_functions) if active_functions else 0
            
            file_list.append(source_file_dict)
    
    # Group files by directories
    dir_groups = {}
    for file in file_list:
        dirname = file['dirname']
        if dirname not in dir_groups:
            dir_groups[dirname] = []
        dir_groups[dirname].append(file)
    
    # Calculate metrics for dashboard (only active functions)
    complexity_data = []
    comment_data = []
    depth_data = []
    pointer_data = []
    directives_data = []
    logical_ops_data = []
    conditional_data = []
    
    for file in file_list:
        active_functions = [f for f in file['functions'] if not f['in_disable_block']]
        if active_functions:
            complexity_data.extend([f['cyclomatic_complexity'] for f in active_functions])
            comment_data.append(file['comment_percentage'])
            depth_data.append(file['max_block_depth'])
            pointer_data.append(file['pointer_operations'])
            directives_data.append(file['preprocessor_directives'])
            logical_ops_data.append(file['logical_operators'])
            conditional_data.append(file['conditional_statements'])
    
    # Prepare comment distribution data
    comment_ranges = {
        '0-10': sum(1 for p in comment_data if p <= 10),
        '10-20': sum(1 for p in comment_data if 10 < p <= 20),
        '20-30': sum(1 for p in comment_data if 20 < p <= 30),
        '30-40': sum(1 for p in comment_data if 30 < p <= 40),
        '40-50': sum(1 for p in comment_data if 40 < p <= 50),
        '50+': sum(1 for p in comment_data if p > 50)
    }
    
    # Prepare depth vs pointers data
    depth_pointers_data = [
        {'x': f['pointer_operations'], 'y': f['max_block_depth'], 'file': f['basename']} 
        for f in file_list
    ]
    
    # Prepare complexity vs nloc data (only active functions)
    complexity_nloc_data = []
    top_complex_functions = []
    
    for file in file_list:
        for func in file['functions']:
            if not func['in_disable_block']:  # Only active functions
                complexity_nloc_data.append({
                    'x': func['nloc'],
                    'y': func['cyclomatic_complexity'],
                    'function': func['name'],
                    'file': file['basename']
                })
                
                top_complex_functions.append({
                    'name': func['name'],
                    'complexity': func['cyclomatic_complexity'],
                    'nloc': func['nloc'],
                    'file': file['basename'],
                    'filepath': file['filename']
                })
    
    # Get top 5 most complex functions (only active)
    top_complex_functions.sort(key=lambda x: -x['complexity'])
    top_complex_functions = top_complex_functions[:5]
    
    # Get files with min/max comments
    files_sorted_by_comments = sorted(file_list, key=lambda x: x['comment_percentage'])
    min_comments_files = files_sorted_by_comments[:5]
    max_comments_files = files_sorted_by_comments[-5:]
    max_comments_files.reverse()
    
    # Calculate code/comment/empty ratio
    total_code_lines = sum(f['lines_of_code'] for f in file_list)
    total_comment_lines = sum(f['comment_lines'] for f in file_list)
    total_empty_lines = sum(f['total_lines'] - f['lines_of_code'] - f['comment_lines'] for f in file_list)
    
    code_ratio = {
        'code': total_code_lines,
        'comments': total_comment_lines,
        'empty': total_empty_lines
    }
    
    # Calculate directory complexity stats (only active functions)
    dir_complexity_stats = []
    for dirname, files in dir_groups.items():
        total_complexity = sum(f['avg_complexity'] for f in files)
        total_files = len(files)
        avg_complexity = total_complexity / total_files if total_files else 0
        dir_complexity_stats.append({
            'name': dirname,
            'avg_complexity': avg_complexity,
            'file_count': total_files
        })
    
    # Sort directories by complexity
    dir_complexity_stats.sort(key=lambda x: -x['avg_complexity'])
    
    # Update file metrics to exclude disabled functions
    total_complexity = 0
    total_functions = 0
    total_disabled_functions = 0
    problem_files = 0
    total_comments = 0
    total_depth = 0
    total_pointers = 0
    total_directives = 0
    total_logical_ops = 0
    total_conditionals = 0
    
    directory_stats = []
    
    for dirname, files in dir_groups.items():
        dir_complexity = 0
        dir_max_complexity = 0
        dir_functions = 0
        dir_disabled_functions = 0
        dir_problem_functions = 0
        dir_comments = 0
        dir_depth = 0
        dir_pointers = 0
        dir_directives = 0
        dir_logical_ops = 0
        dir_conditionals = 0
        
        for file in files:
            # Separate active and disabled functions
            active_functions = [f for f in file['functions'] if not f['in_disable_block']]
            disabled_functions = [f for f in file['functions'] if f['in_disable_block']]
            
            # Calculate metrics only for active functions
            file['problem_functions'] = sum(
                1 for func in active_functions 
                if func['cyclomatic_complexity'] > options.thresholds['cyclomatic_complexity']
            )
            file['max_complexity'] = max(
                (func['cyclomatic_complexity'] for func in active_functions),
                default=0
            )
            file['avg_complexity'] = sum(
                func['cyclomatic_complexity'] for func in active_functions
            ) / len(active_functions) if active_functions else 0
            
            # Count disabled functions
            file['disabled_functions_count'] = len(disabled_functions)
            file['active_functions_count'] = len(active_functions)
            
            dir_complexity += file['avg_complexity']
            dir_max_complexity = max(dir_max_complexity, file['max_complexity'])
            dir_functions += file['active_functions_count']
            dir_disabled_functions += file['disabled_functions_count']
            dir_problem_functions += file['problem_functions']
            dir_comments += file['comment_percentage']
            dir_depth += file['max_block_depth']
            dir_pointers += file['pointer_operations']
            dir_directives += file['preprocessor_directives']
            dir_logical_ops += file['logical_operators']
            dir_conditionals += file['conditional_statements']
            
            total_complexity += file['avg_complexity']
            total_functions += file['active_functions_count']
            total_disabled_functions += file['disabled_functions_count']
            total_comments += file['comment_percentage']
            total_depth += file['max_block_depth']
            total_pointers += file['pointer_operations']
            total_directives += file['preprocessor_directives']
            total_logical_ops += file['logical_operators']
            total_conditionals += file['conditional_statements']
            
            if file['max_complexity'] > options.thresholds['cyclomatic_complexity']:
                problem_files += 1
        
        directory_stats.append({
            'name': dirname,
            'max_complexity': dir_max_complexity,
            'avg_complexity': dir_complexity / len(files) if files else 0,
            'total_functions': dir_functions,
            'disabled_functions': dir_disabled_functions,
            'problem_functions': dir_problem_functions,
            'file_count': len(files),
            'avg_comments': dir_comments / len(files) if files else 0,
            'avg_depth': dir_depth / len(files) if files else 0,
            'avg_pointers': dir_pointers / len(files) if files else 0,
            'avg_directives': dir_directives / len(files) if files else 0,
            'avg_logical_ops': dir_logical_ops / len(files) if files else 0,
            'avg_conditionals': dir_conditionals / len(files) if files else 0
        })
    
    avg_complexity = total_complexity / len(file_list) if file_list else 0
    avg_comments = total_comments / len(file_list) if file_list else 0
    avg_depth = total_depth / len(file_list) if file_list else 0
    avg_pointers = total_pointers / len(file_list) if file_list else 0
    avg_directives = total_directives / len(file_list) if file_list else 0
    avg_logical_ops = total_logical_ops / len(file_list) if file_list else 0
    avg_conditionals = total_conditionals / len(file_list) if file_list else 0
    
    # Combine thresholds with new values
    full_thresholds = {
        'cyclomatic_complexity': 20,
        'nloc': 100,
        'comment_percentage': 0,  # Не учитываем threshold, только отображаем
        'max_block_depth': 3,
        'pointer_operations': 70,
        'preprocessor_directives': 30,
        'logical_operators': options.thresholds.get('logical_operators', Config.THRESHOLDS['logical_operators']),
        'conditional_statements': options.thresholds.get('conditional_statements', Config.THRESHOLDS['conditional_statements']),
        'parameter_count': 3,
        'function_count': 20,
        'token_count': 500
    }
    
    # Prepare dashboard data
    dashboard_data = {
        'complexity_distribution': {
            'low': sum(1 for c in complexity_data if c <= full_thresholds['cyclomatic_complexity'] * 0.5),
            'medium': sum(1 for c in complexity_data if full_thresholds['cyclomatic_complexity'] * 0.5 < c <= full_thresholds['cyclomatic_complexity']),
            'high': sum(1 for c in complexity_data if c > full_thresholds['cyclomatic_complexity'])
        },
        'avg_metrics': {
            'complexity': sum(complexity_data)/len(complexity_data) if complexity_data else 0,
            'comments': sum(comment_data)/len(comment_data) if comment_data else 0,
            'depth': sum(depth_data)/len(depth_data) if depth_data else 0,
            'pointers': sum(pointer_data)/len(pointer_data) if pointer_data else 0,
            'directives': sum(directives_data)/len(directives_data) if directives_data else 0,
            'logical_ops': sum(logical_ops_data)/len(logical_ops_data) if logical_ops_data else 0,
            'conditionals': sum(conditional_data)/len(conditional_data) if conditional_data else 0
        },
        'comment_ranges': comment_ranges,
        'depth_pointers_data': depth_pointers_data,
        'complexity_nloc_data': complexity_nloc_data,
        'thresholds': full_thresholds
    }
    
    output = Template(TEMPLATE).render(
            title='xLizard + SourceMonitor code report',
            date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            thresholds=full_thresholds, 
            dir_groups=dir_groups,
            total_files=len(file_list),
            problem_files=problem_files,
            avg_complexity=round(avg_complexity, 2),
            avg_comments=round(avg_comments, 2),
            avg_depth=round(avg_depth, 2),
            avg_pointers=round(avg_pointers, 2),
            avg_directives=round(avg_directives, 2),
            avg_logical_ops=round(avg_logical_ops, 2),
            avg_conditionals=round(avg_conditionals, 2),
            total_functions=total_functions,
            total_disabled_functions=total_disabled_functions,
            directory_stats=sorted(directory_stats, key=lambda x: -x['max_complexity']),
            dashboard_data=dashboard_data,
            top_complex_functions=top_complex_functions,
            min_comments_files=min_comments_files,
            max_comments_files=max_comments_files,
            code_ratio=code_ratio,
            dir_complexity_stats=dir_complexity_stats)
    print(output)
    return 0

# ... остальные функции (_get_function_code, _create_dict, _is_in_disable_block) остаются без изменений

def _get_function_code(file_path, start_line, end_line):
    """Чтение кода функции с поддержкой разных кодировок"""
    try:
        # Пробуем разные кодировки
        encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    lines = f.readlines()
                    return ''.join(lines[start_line-1:end_line])
            except UnicodeDecodeError:
                continue
        
        # Fallback: бинарное чтение
        with open(file_path, 'rb') as f:
            binary_content = f.read()
            content = binary_content.decode('utf-8', errors='ignore')
            lines = content.split('\n')
            return '\n'.join(lines[start_line-1:end_line])
            
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return ""
    
def _create_dict(source_function, file_path):
    func_dict = {
        'name': source_function.name,
        'cyclomatic_complexity': source_function.cyclomatic_complexity,
        'nloc': source_function.nloc,
        'token_count': source_function.token_count,
        'parameter_count': source_function.parameter_count,
        'start_line': source_function.start_line,
        'end_line': source_function.end_line
    }
    
    # Получаем код функции
    func_code = _get_function_code(file_path, source_function.start_line, source_function.end_line)
    
    if func_code:
        # Используем прямое обращение к статическому методу
        func_dict['max_depth'] = FileAnalyzer._calculate_block_depth_accurate(func_code)
    else:
        func_dict['max_depth'] = 0
        
    # Проверяем, находится ли функция в disable-блоке
    func_dict['in_disable_block'] = _is_in_disable_block(file_path, source_function.start_line, source_function.end_line)
        
    return func_dict

def _is_in_disable_block(file_path, start_line, end_line):
    """Проверяет, находится ли функция между XLIZARD_DISABLE и XLIZARD_ENABLE"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        in_disable_block = False
        disable_start = 0
        
        # Проверяем все строки до начала функции
        for i, line in enumerate(lines[:start_line], 1):
            if 'XLIZARD_DISABLE' in line:
                in_disable_block = True
                disable_start = i
            elif 'XLIZARD_ENABLE' in line and in_disable_block:
                in_disable_block = False
                
        # Если функция начинается в disable-блоке, помечаем ее
        if in_disable_block:
            return True
            
        # Проверяем, не начинается ли disable-блок внутри функции
        for i, line in enumerate(lines[start_line-1:end_line], start_line):
            if 'XLIZARD_DISABLE' in line:
                return True
                
    except Exception:
        pass
        
    return False

TEMPLATE = '''<!DOCTYPE HTML PUBLIC
"-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --glass-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.2);
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --danger-gradient: linear-gradient(135deg, #ff057c 0%, #8d0b93 100%);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.8);
        --text-tertiary: rgba(255, 255, 255, 0.6);
        --bg-primary: #0f0f1a;
        --bg-secondary: #1a1a2a;
        --border-radius: 12px;
        --border-radius-sm: 6px;
        
        /* Badge colors for dark theme */
        --badge-safe-bg: rgba(67, 233, 123, 0.15);
        --badge-safe-border: rgba(67, 233, 123, 0.4);
        --badge-safe-text: #43e97b;
        
        --badge-warning-bg: rgba(250, 112, 154, 0.15);
        --badge-warning-border: rgba(250, 112, 154, 0.4);
        --badge-warning-text: #fa709a;
        
        --badge-danger-bg: rgba(255, 5, 124, 0.15);
        --badge-danger-border: rgba(255, 5, 124, 0.4);
        --badge-danger-text: #ff057c;
        
        --badge-info-bg: rgba(79, 172, 254, 0.15);
        --badge-info-border: rgba(79, 172, 254, 0.4);
        --badge-info-text: #4facfe;

        /* Navigation colors for dark theme */
        --nav-bg: rgba(255, 255, 255, 0.05);
        --nav-border: rgba(255, 255, 255, 0.1);
        --nav-text: rgba(255, 255, 255, 0.8);
        --nav-active-bg: rgba(103, 126, 234, 0.2);
        --nav-active-border: rgba(103, 126, 234, 0.4);
        --nav-active-text: #ffffff;
    }

    [data-theme="light"] {
        --glass-bg: rgba(255, 255, 255, 0.8);
        --glass-border: rgba(0, 0, 0, 0.1);
        --glass-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
        --text-primary: #1a1a2a;
        --text-secondary: rgba(26, 26, 42, 0.8);
        --text-tertiary: rgba(26, 26, 42, 0.6);
        --bg-primary: #f8f9fa;
        --bg-secondary: #ffffff;
        
        /* Badge colors for light theme */
        --badge-safe-bg: rgba(67, 233, 123, 0.15);
        --badge-safe-border: rgba(67, 233, 123, 0.5);
        --badge-safe-text: #27ae60;
        
        --badge-warning-bg: rgba(250, 112, 154, 0.15);
        --badge-warning-border: rgba(250, 112, 154, 0.5);
        --badge-warning-text: #e74c3c;
        
        --badge-danger-bg: rgba(255, 5, 124, 0.15);
        --badge-danger-border: rgba(255, 5, 124, 0.5);
        --badge-danger-text: #c0392b;
        
        --badge-info-bg: rgba(79, 172, 254, 0.15);
        --badge-info-border: rgba(79, 172, 254, 0.5);
        --badge-info-text: #2980b9;

        /* Navigation colors for light theme */
        --nav-bg: rgba(0, 0, 0, 0.05);
        --nav-border: rgba(0, 0, 0, 0.1);
        --nav-text: rgba(26, 26, 42, 0.8);
        --nav-active-bg: rgba(103, 126, 234, 0.15);
        --nav-active-border: rgba(103, 126, 234, 0.3);
        --nav-active-text: #667eea;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
        line-height: 1.5;
        min-height: 100vh;
        overflow-x: hidden;
        transition: all 0.3s ease;
    }

    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 1rem;
    }

    /* Glass Elements */
    .glass-header, .glass-nav, .glass-card, .metric-card, .chart-container, .directory-header, .file-card, .glass-search, .glass-footer {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        box-shadow: var(--glass-shadow);
    }

    /* Scroll to Top Button */
    .scroll-to-top {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background: var(--primary-gradient);
        border: none;
        border-radius: 50%;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        opacity: 0;
        visibility: hidden;
        transform: translateY(20px);
        transition: all 0.3s ease;
        z-index: 1000;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .scroll-to-top.visible {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }

    .scroll-to-top:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
    }

    .scroll-to-top:active {
        transform: translateY(0);
    }

    .glass-header {
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        position: relative;
        z-index: 2;
    }

    .header-text {
        flex: 1;
    }

    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }

    .logo {
        width: 40px;
        height: 40px;
        background: var(--primary-gradient);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
    }

    .report-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }

    .report-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }

    .header-meta {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .header-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .glass-button {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius-sm);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .glass-button:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    /* Navigation */
    .glass-nav {
        display: flex;
        padding: 0.5rem;
        margin-bottom: 1rem;
        gap: 0.5rem;
        background: var(--nav-bg);
        border: 1px solid var(--nav-border);
    }

    .nav-item {
        padding: 0.75rem 1.5rem;
        cursor: pointer;
        border-radius: var(--border-radius-sm);
        transition: all 0.2s ease;
        color: var(--nav-text);
        font-weight: 500;
        border: none;
        background: none;
        flex: 1;
        text-align: center;
        border: 1px solid transparent;
    }

    .nav-item:hover {
        color: var(--text-primary);
        background: rgba(255, 255, 255, 0.05);
        border-color: var(--nav-border);
    }

    .nav-item.active {
        color: var(--nav-active-text);
        background: var(--nav-active-bg);
        font-weight: 600;
        border-color: var(--nav-active-border);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    /* Cards */
    .glass-card {
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--glass-border);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        box-shadow: var(--glass-shadow);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
        line-height: 1;
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    /* Charts */
    .charts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .chart-container {
        padding: 1.5rem;
        transition: all 0.2s ease;
    }

    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }

    .chart-wrapper {
        position: relative;
        height: 250px;
        width: 100%;
    }

    /* Directory Groups */
    .directory-group {
        margin-bottom: 1.5rem;
    }

    .directory-header {
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .directory-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    .directory-count {
        background: var(--primary-gradient);
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
    }

    /* File Cards */
    .file-card {
        margin-bottom: 1rem;
        overflow: hidden;
        transition: all 0.2s ease;
    }

    .file-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 1rem 1.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        background: rgba(255, 255, 255, 0.02);
        flex-direction: column;
        gap: 0.75rem;
    }

    .file-header:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .file-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
    }

    .file-icon {
        width: 20px;
        height: 20px;
        background: var(--primary-gradient);
        mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/></svg>');
        -webkit-mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/></svg>');
        mask-repeat: no-repeat;
        -webkit-mask-repeat: no-repeat;
        flex-shrink: 0;
    }

    .file-name {
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
    }

    .file-metrics {
        display: flex;
        gap: 0.5rem;
        width: 100%;
        flex-wrap: wrap;
    }

    /* Badges */
    .glass-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        transition: all 0.2s ease;
        white-space: nowrap;
        position: relative;
        border: 1px solid;
        backdrop-filter: none;
    }

    .glass-badge.safe {
        background: var(--badge-safe-bg);
        border-color: var(--badge-safe-border);
        color: var(--badge-safe-text);
    }

    .glass-badge.warning {
        background: var(--badge-warning-bg);
        border-color: var(--badge-warning-border);
        color: var(--badge-warning-text);
    }

    .glass-badge.danger {
        background: var(--badge-danger-bg);
        border-color: var(--badge-danger-border);
        color: var(--badge-danger-text);
    }

    .glass-badge.info {
        background: var(--badge-info-bg);
        border-color: var(--badge-info-border);
        color: var(--badge-info-text);
    }

    .glass-badge:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .badge-value {
        font-weight: 700;
        margin-right: 0.25rem;
    }

    .badge-label {
        font-size: 0.75rem;
        opacity: 0.9;
    }

    .file-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
        background: rgba(255, 255, 255, 0.02);
    }

    .file-content.expanded {
        max-height: 2000px;
    }

    .file-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }

    .file-table th {
        text-align: left;
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid var(--glass-border);
    }

    .file-table td {
        padding: 0.75rem 1.5rem;
        border-bottom: 1px solid var(--glass-border);
    }

    .file-table tr:last-child td {
        border-bottom: none;
    }

    .function-name {
        font-family: 'Fira Code', 'Consolas', monospace;
        color: var(--text-primary);
        font-size: 0.9rem;
    }

    .metric-value-high {
        color: #ff057c;
        font-weight: 600;
    }

    .metric-value-low {
        color: #43e97b;
        font-weight: 500;
    }

    .metric-value-warning {
        color: #fa709a;
        font-weight: 600;
    }

    .function-disabled {
        background: rgba(255, 165, 0, 0.05);
        border-left: 3px solid #ff8c00;
    }

    /* Tooltips */
    .tooltip-icon {
        cursor: pointer;
        width: 16px;
        height: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: var(--text-secondary);
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 0.25rem;
        transition: all 0.2s ease;
    }

    .tooltip-icon:hover {
        background: var(--primary-gradient);
        color: white;
        border-color: transparent;
    }

    .custom-tooltip {
        position: absolute;
        z-index: 1000;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-radius: var(--border-radius-sm);
        font-size: 0.8rem;
        max-width: 250px;
        box-shadow: var(--glass-shadow);
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.2s ease;
        pointer-events: none;
        line-height: 1.4;
    }

    .custom-tooltip.visible {
        opacity: 1;
        transform: translateY(0);
    }

    /* Search */
    .glass-search {
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .search-container {
        display: flex;
        align-items: center;
        position: relative;
    }

    .search-icon {
        position: absolute;
        left: 12px;
        color: var(--text-secondary);
        z-index: 2;
    }

    .search-input {
        width: 100%;
        padding: 0.75rem 2.5rem;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-sm);
        color: var(--text-primary);
        font-family: inherit;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }

    .search-input:focus {
        outline: none;
        border-color: rgba(103, 126, 234, 0.5);
        background: rgba(255, 255, 255, 0.15);
    }

    .clear-search {
        position: absolute;
        right: 12px;
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 4px;
        border-radius: 50%;
    }

    /* Search highlight */
    .highlight {
        background: linear-gradient(135deg, #ffd700 0%, #ffb700 100%);
        color: #000 !important;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: 600;
    }

    .search-match {
        animation: highlightPulse 2s ease-in-out;
    }

    @keyframes highlightPulse {
        0%, 100% { background-color: transparent; }
        50% { background-color: rgba(255, 215, 0, 0.3); }
    }

    /* Footer */
    .glass-footer {
        padding: 1.5rem;
        margin-top: 2rem;
        text-align: center;
        color: var(--text-secondary);
    }

    .glass-footer a {
        color: var(--text-primary);
        text-decoration: none;
        font-weight: 500;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Tab Content */
    .tab-content {
        display: none;
    }

    .tab-content.active {
        display: block;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Performance Optimizations */
    .chart-container canvas {
        max-width: 100%;
        height: auto;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .container {
            padding: 0.5rem;
        }
        
        .glass-header {
            padding: 1rem;
        }
        
        .header-content {
            flex-direction: column;
        }
        
        .report-title {
            font-size: 1.5rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr 1fr;
        }
        
        .charts-grid {
            grid-template-columns: 1fr;
        }
        
        .chart-wrapper {
            height: 200px;
        }
        
        .file-header {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .file-metrics {
            justify-content: flex-start;
        }
        
        .glass-nav {
            flex-direction: column;
        }
        
        .scroll-to-top {
            bottom: 20px;
            right: 20px;
            width: 45px;
            height: 45px;
            font-size: 18px;
        }
    }

    @media (max-width: 480px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .file-table {
            font-size: 0.8rem;
        }
        
        .file-table th,
        .file-table td {
            padding: 0.5rem 1rem;
        }
        
        .file-metrics {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .glass-badge {
            width: 100%;
            justify-content: space-between;
        }
        
        .scroll-to-top {
            bottom: 15px;
            right: 15px;
            width: 40px;
            height: 40px;
            font-size: 16px;
        }
    }
  </style>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Scroll to Top Button -->
    <button class="scroll-to-top" id="scrollToTop" aria-label="Scroll to top">
        ↑
    </button>

    <div class="container">
        <!-- Glass Header -->
        <div class="glass-header">
            <div class="header-content">
                <div class="header-text">
                    <div class="logo-container">
                        <div class="logo">🦎</div>
                        <h1 class="report-title">{{ title }}</h1>
                    </div>
                    <p class="report-subtitle">Code quality analysis report</p>
                    <div class="header-meta">
                        <div class="meta-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                            </svg>
                            {{ total_files }} files
                        </div>
                        <div class="meta-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                                <path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                            </svg>
                            {{ date }}
                        </div>
                    </div>
                </div>
                <div class="header-actions">
                    <button class="glass-button" id="themeToggle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20 8.69V4h-4.69L12 .69 8.69 4H4v4.69L.69 12 4 15.31V20h4.69L12 23.31 15.31 20H20v-4.69L23.31 12 20 8.69zM12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm0-10c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4z"/>
                        </svg>
                        Theme
                    </button>
                </div>
            </div>
        </div>

        <!-- Navigation -->
        <div class="glass-nav">
            <button class="nav-item active" data-tab="dashboardTab">Dashboard</button>
            <button class="nav-item" data-tab="filesTab">Files</button>
            <button class="nav-item" data-tab="advancedTab">Advanced</button>
        </div>

        <!-- Search -->
        <div class="glass-search">
            <div class="search-container">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" class="search-icon">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
                <input type="text" id="searchInput" placeholder="Search files and functions..." class="search-input">
                <button id="clearSearch" class="clear-search" style="display: none;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
        </div>

        <!-- Dashboard Tab -->
        <div class="tab-content active" id="dashboardTab">
            <!-- Metrics Cards -->
            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Project Overview</h3>
                </div>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">📊</div>
                        <div class="metric-value">{{ avg_complexity|round(1) }}</div>
                        <div class="metric-label">Average Complexity</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">💬</div>
                        <div class="metric-value">{{ avg_comments|round(1) }}%</div>
                        <div class="metric-label">Average Comments</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">📏</div>
                        <div class="metric-value">{{ avg_depth|round(1) }}</div>
                        <div class="metric-label">Average Depth</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">⚡</div>
                        <div class="metric-value">{{ total_functions }}</div>
                        <div class="metric-label">Total Functions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">🔧</div>
                        <div class="metric-value">{{ total_disabled_functions }}</div>
                        <div class="metric-label">Disabled Functions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">⚠️</div>
                        <div class="metric-value">{{ problem_files }}</div>
                        <div class="metric-label">Problem Files</div>
                    </div>
                </div>
            </div>

            <!-- Charts -->
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Complexity Distribution</div>
                    <div class="chart-wrapper">
                        <canvas id="complexityChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Metrics Overview</div>
                    <div class="chart-wrapper">
                        <canvas id="metricsChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Comments Distribution</div>
                    <div class="chart-wrapper">
                        <canvas id="commentsChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Depth vs Pointers</div>
                    <div class="chart-wrapper">
                        <canvas id="depthPointersChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Files Tab -->
        <div class="tab-content" id="filesTab">
            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Project Files</h3>
                    <div class="directory-count">{{ total_files }} files</div>
                </div>
                
                {% for dirname, files in dir_groups.items() %}
                <div class="directory-group">
                    <div class="directory-header">
                        <h3 class="directory-name">{{ dirname }}</h3>
                        <div class="directory-count">{{ files|length }} files</div>
                    </div>
                    
                    {% for file in files %}
                    <div class="file-card">
                        <div class="file-header" onclick="toggleFile(this)">
                            <div class="file-title">
                                <div class="file-icon"></div>
                                <h4 class="file-name">{{ file.basename }}</h4>
                            </div>
                            <div class="file-metrics">
                                <div class="glass-badge {% if file.max_complexity <= thresholds.cyclomatic_complexity*0.5 %}safe{% elif file.max_complexity <= thresholds.cyclomatic_complexity %}warning{% else %}danger{% endif %}">
                                    <span class="badge-value">{{ file.max_complexity }}</span>
                                    <span class="badge-label">Max CC</span>
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds.cyclomatic_complexity*0.5)|round }} (safe), ≤{{ thresholds.cyclomatic_complexity }} (warning), >{{ thresholds.cyclomatic_complexity }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.active_functions_count <= thresholds.function_count*0.5 %}safe{% elif file.active_functions_count <= thresholds.function_count %}warning{% else %}danger{% endif %}">
                                    <span class="badge-value">{{ file.active_functions_count }}</span>
                                    <span class="badge-label">Active Funcs</span>
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds.function_count*0.5)|round }} (safe), ≤{{ thresholds.function_count }} (warning), >{{ thresholds.function_count }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.disabled_functions_count > 0 %}warning{% else %}safe{% endif %}">
                                    <span class="badge-value">{{ file.disabled_functions_count }}</span>
                                    <span class="badge-label">DSB Func</span>
                                    <div class="tooltip-icon" data-tooltip="Functions disabled by XLIZARD_DISABLE directive">?</div>
                                </div>
                                <div class="glass-badge {% if file.max_block_depth <= thresholds.max_block_depth*0.7 %}safe{% elif file.max_block_depth <= thresholds.max_block_depth %}warning{% else %}danger{% endif %}">
                                    <span class="badge-value">{{ file.max_block_depth }}</span>
                                    <span class="badge-label">Max Depth</span>
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds.max_block_depth*0.7)|round }} (safe), ≤{{ thresholds.max_block_depth }} (warning), >{{ thresholds.max_block_depth }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.pointer_operations <= thresholds.pointer_operations*0.5 %}safe{% elif file.pointer_operations <= thresholds.pointer_operations %}warning{% else %}danger{% endif %}">
                                    <span class="badge-value">{{ file.pointer_operations }}</span>
                                    <span class="badge-label">Ptr Ops</span>
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds.pointer_operations*0.5)|round }} (safe), ≤{{ thresholds.pointer_operations }} (warning), >{{ thresholds.pointer_operations }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.preprocessor_directives <= thresholds.preprocessor_directives*0.5 %}safe{% elif file.preprocessor_directives <= thresholds.preprocessor_directives %}warning{% else %}danger{% endif %}">
                                    <span class="badge-value">{{ file.preprocessor_directives }}</span>
                                    <span class="badge-label">PP Directives</span>
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds.preprocessor_directives*0.5)|round }} (safe), ≤{{ thresholds.preprocessor_directives }} (warning), >{{ thresholds.preprocessor_directives }} (danger)">?</div>
                                </div>
                                <div class="glass-badge info">
                                    <span class="badge-value">{{ file.comment_percentage|round(1) }}%</span>
                                    <span class="badge-label">Comments</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="file-content">
                            {% if file.functions %}
                            <table class="file-table">
                                <thead>
                                    <tr>
                                        <th>Function</th>
                                        <th>
                                            CCN <div class="tooltip-icon" data-tooltip="Cyclomatic Complexity Number">?</div>
                                        </th>
                                        <th>
                                            LOC <div class="tooltip-icon" data-tooltip="Lines of Code">?</div>
                                        </th>
                                        <th>
                                            Tokens <div class="tooltip-icon" data-tooltip="Number of tokens">?</div>
                                        </th>
                                        <th>
                                            Params <div class="tooltip-icon" data-tooltip="Number of parameters">?</div>
                                        </th>
                                        <th>
                                            Depth <div class="tooltip-icon" data-tooltip="Maximum nesting depth">?</div>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for func in file.functions %}
                                    <tr class="{% if func.in_disable_block %}function-disabled{% endif %}">
                                        <td class="function-name">
                                            {{ func.name }}
                                            {% if func.in_disable_block %}
                                            <div class="tooltip-icon" data-tooltip="Function analysis disabled by XLIZARD_DISABLE directive">🟠</div>
                                            {% endif %}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.cyclomatic_complexity > thresholds.cyclomatic_complexity %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.cyclomatic_complexity }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.nloc > thresholds.nloc %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.nloc }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.token_count > thresholds.token_count %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.token_count }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.parameter_count > thresholds.parameter_count %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.parameter_count }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.max_depth > thresholds.max_block_depth %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.max_depth }}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                            {% else %}
                            <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
                                No functions found
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Advanced Tab -->
        <div class="tab-content" id="advancedTab">
            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Top Complex Functions</h3>
                </div>
                <div style="overflow-x: auto;">
                    <table class="file-table">
                        <thead>
                            <tr>
                                <th>Function</th>
                                <th>File</th>
                                <th>Complexity</th>
                                <th>Lines</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for func in top_complex_functions %}
                            <tr>
                                <td class="function-name">{{ func.name }}</td>
                                <td>{{ func.file }}</td>
                                <td class="metric-value-high">{{ func.complexity }}</td>
                                <td>{{ func.nloc }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Directory Complexity</h3>
                </div>
                <div style="overflow-x: auto;">
                    <table class="file-table">
                        <thead>
                            <tr>
                                <th>Directory</th>
                                <th>Avg Complexity</th>
                                <th>Files</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for dir in dir_complexity_stats %}
                            <tr>
                                <td>{{ dir.name }}</td>
                                <td class="{% if dir.avg_complexity > thresholds.cyclomatic_complexity %}metric-value-high{% else %}metric-value-low{% endif %}">
                                    {{ dir.avg_complexity|round(1) }}
                                </td>
                                <td>{{ dir.file_count }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="glass-footer">
            Generated on {{ date }} by <a href="http://www.xlizard.ws/" target="_blank">xlizard</a>
        </div>
    </div>

    <script>
    // Global chart instances storage
    const chartInstances = {
        complexityChart: null,
        metricsChart: null,
        commentsChart: null,
        depthPointersChart: null
    };

    // Function to update chart colors based on theme
    function updateChartColors() {
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        const textColor = isDark ? '#ffffff' : '#1a1a2a';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        const fontFamily = 'Inter, sans-serif';

        // Update all existing charts
        Object.entries(chartInstances).forEach(([chartName, chart]) => {
            if (chart) {
                // Update scales colors
                if (chart.options.scales) {
                    Object.values(chart.options.scales).forEach(scale => {
                        if (scale.ticks) {
                            scale.ticks.color = textColor;
                        }
                        if (scale.grid) {
                            scale.grid.color = gridColor;
                        }
                        if (scale.title) {
                            scale.title.color = textColor;
                        }
                    });
                }

                // Update legend colors
                if (chart.options.plugins && chart.options.plugins.legend) {
                    chart.options.plugins.legend.labels.color = textColor;
                }

                // Update tooltip colors
                if (chart.options.plugins && chart.options.plugins.tooltip) {
                    chart.options.plugins.tooltip.bodyColor = textColor;
                    chart.options.plugins.tooltip.titleColor = textColor;
                }

                chart.update('none'); // Update without animation for better performance
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize charts only when needed
        let chartsInitialized = {
            dashboard: false,
            advanced: false
        };

        // Theme toggle with immediate update
        const themeToggle = document.getElementById('themeToggle');
        
        function applyTheme(theme) {
            document.body.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            
            // Force CSS repaint
            document.body.style.opacity = '0.99';
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 10);
            
            // Update charts immediately with proper theme colors
            updateChartColors();
        }

        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });

        // Set initial theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        applyTheme(savedTheme);

        // Scroll to Top Functionality
        const scrollToTopBtn = document.getElementById('scrollToTop');

        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add('visible');
            } else {
                scrollToTopBtn.classList.remove('visible');
            }
        });

        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        // Tooltip system
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        document.body.appendChild(tooltip);

        document.querySelectorAll('.tooltip-icon').forEach(icon => {
            icon.addEventListener('mouseenter', function(e) {
                const text = this.getAttribute('data-tooltip');
                const rect = this.getBoundingClientRect();
                
                tooltip.textContent = text;
                tooltip.style.left = `${rect.left + window.scrollX}px`;
                tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
                tooltip.classList.add('visible');
            });

            icon.addEventListener('mouseleave', function() {
                tooltip.classList.remove('visible');
            });
        });

        // Navigation
        const navItems = document.querySelectorAll('.nav-item');
        const tabContents = document.querySelectorAll('.tab-content');

        function switchTab(tabId) {
            navItems.forEach(nav => nav.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
            document.getElementById(tabId).classList.add('active');
            
            // Initialize charts for active tab
            if (tabId === 'dashboardTab' && !chartsInitialized.dashboard) {
                initDashboardCharts();
                chartsInitialized.dashboard = true;
            } else if (tabId === 'advancedTab' && !chartsInitialized.advanced) {
                initAdvancedCharts();
                chartsInitialized.advanced = true;
            }
        }

        navItems.forEach(item => {
            item.addEventListener('click', function() {
                switchTab(this.getAttribute('data-tab'));
            });
        });

        // Initialize dashboard charts on first load
        initDashboardCharts();
        chartsInitialized.dashboard = true;

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const clearSearch = document.getElementById('clearSearch');

        function performSearch() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            clearSearch.style.display = searchTerm ? 'block' : 'none';
            
            // Remove previous highlights
            document.querySelectorAll('.highlight').forEach(el => {
                el.outerHTML = el.innerHTML;
            });
            
            let hasAnyMatch = false;
            let firstMatchElement = null;
            
            if (searchTerm) {
                // Search in file names
                document.querySelectorAll('.file-name').forEach(element => {
                    const filename = element.textContent.toLowerCase();
                    if (filename.includes(searchTerm)) {
                        const highlighted = element.textContent.replace(
                            new RegExp(searchTerm, 'gi'), 
                            match => '<span class="highlight">' + match + '</span>'
                        );
                        element.innerHTML = highlighted;
                        const fileCard = element.closest('.file-card');
                        fileCard.classList.add('search-match');
                        hasAnyMatch = true;
                        
                        // Auto-expand file
                        const fileHeader = fileCard.querySelector('.file-header');
                        if (fileHeader && !fileHeader.classList.contains('expanded')) {
                            toggleFile(fileHeader);
                        }
                        
                        // Remember first match for scrolling
                        if (!firstMatchElement) {
                            firstMatchElement = fileCard;
                        }
                    }
                });
                
                // Search in function names
                document.querySelectorAll('.function-name').forEach(element => {
                    const funcName = element.textContent.toLowerCase();
                    if (funcName.includes(searchTerm)) {
                        const highlighted = element.textContent.replace(
                            new RegExp(searchTerm, 'gi'), 
                            match => '<span class="highlight">' + match + '</span>'
                        );
                        element.innerHTML = highlighted;
                        const fileCard = element.closest('.file-card');
                        fileCard.classList.add('search-match');
                        hasAnyMatch = true;
                        
                        // Auto-expand file
                        const fileHeader = fileCard.querySelector('.file-header');
                        if (fileHeader && !fileHeader.classList.contains('expanded')) {
                            toggleFile(fileHeader);
                        }
                        
                        // Remember first match for scrolling
                        if (!firstMatchElement) {
                            firstMatchElement = element;
                        }
                    }
                });
                
                // Hide files without matches
                document.querySelectorAll('.file-card').forEach(card => {
                    const hasMatch = card.querySelector('.highlight') !== null;
                    card.style.display = hasMatch ? '' : 'none';
                });
                
                // Scroll to first match
                if (firstMatchElement) {
                    setTimeout(() => {
                        firstMatchElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 100);
                }
            } else {
                // Show all files, remove highlights, and collapse all
                document.querySelectorAll('.file-card').forEach(card => {
                    card.style.display = '';
                    card.classList.remove('search-match');
                    
                    // Collapse file if it was expanded by search
                    const fileHeader = card.querySelector('.file-header');
                    if (fileHeader && fileHeader.classList.contains('expanded')) {
                        toggleFile(fileHeader);
                    }
                });
            }
        }

        searchInput.addEventListener('input', performSearch);
        
        clearSearch.addEventListener('click', function() {
            searchInput.value = '';
            clearSearch.style.display = 'none';
            
            // Remove all highlights, show all files, and collapse all
            document.querySelectorAll('.highlight').forEach(el => {
                el.outerHTML = el.innerHTML;
            });
            
            document.querySelectorAll('.file-card').forEach(card => {
                card.style.display = '';
                card.classList.remove('search-match');
                
                // Collapse file if it was expanded by search
                const fileHeader = card.querySelector('.file-header');
                if (fileHeader && fileHeader.classList.contains('expanded')) {
                    toggleFile(fileHeader);
                }
            });
        });

        // Handle Escape key for search
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        });

        // Auto-switch to Files tab when searching
        searchInput.addEventListener('focus', function() {
            if (this.value) {
                switchTab('filesTab');
            }
        });
    });

    function toggleFile(header) {
        const content = header.nextElementSibling;
        const isExpanding = !header.classList.contains('expanded');
        
        header.classList.toggle('expanded');
        content.classList.toggle('expanded');
        
        if (isExpanding) {
            content.style.maxHeight = content.scrollHeight + 'px';
        } else {
            content.style.maxHeight = '0';
        }
    }

    function initDashboardCharts() {
        const dashboardData = {{ dashboard_data|tojson }};
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        const textColor = isDark ? '#ffffff' : '#1a1a2a';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        const fontFamily = 'Inter, sans-serif';

        // Destroy existing charts
        Object.values(chartInstances).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });

        // Complexity Distribution
        const complexityCtx = document.getElementById('complexityChart').getContext('2d');
        chartInstances.complexityChart = new Chart(complexityCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Medium', 'High'],
                datasets: [{
                    data: [
                        dashboardData.complexity_distribution.low,
                        dashboardData.complexity_distribution.medium,
                        dashboardData.complexity_distribution.high
                    ],
                    backgroundColor: ['#43e97b', '#fa709a', '#ff057c']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: textColor,
                            font: {
                                family: fontFamily,
                                size: 12
                            }
                        }
                    }
                }
            }
        });

        // Metrics Comparison
        const metricsCtx = document.getElementById('metricsChart').getContext('2d');
        chartInstances.metricsChart = new Chart(metricsCtx, {
            type: 'bar',
            data: {
                labels: ['Complexity', 'Comments', 'Depth', 'Pointers'],
                datasets: [{
                    label: 'Average',
                    data: [
                        dashboardData.avg_metrics.complexity,
                        dashboardData.avg_metrics.comments,
                        dashboardData.avg_metrics.depth,
                        dashboardData.avg_metrics.pointers
                    ],
                    backgroundColor: 'rgba(103, 126, 234, 0.8)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { 
                            color: gridColor 
                        },
                        ticks: { 
                            color: textColor,
                            font: {
                                family: fontFamily,
                                size: 11
                            }
                        }
                    },
                    x: {
                        grid: { 
                            color: gridColor 
                        },
                        ticks: { 
                            color: textColor,
                            font: {
                                family: fontFamily,
                                size: 11
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: textColor,
                            font: {
                                family: fontFamily,
                                size: 12
                            }
                        }
                    }
                }
            }
        });

        // Comments Distribution
        const commentsCtx = document.getElementById('commentsChart').getContext('2d');
        chartInstances.commentsChart = new Chart(commentsCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(dashboardData.comment_ranges).map(k => k.replace('-', '-') + '%'),
                datasets: [{
                    data: Object.values(dashboardData.comment_ranges),
                    backgroundColor: [
                        'rgba(103, 126, 234, 0.7)',
                        'rgba(67, 233, 123, 0.7)',
                        'rgba(250, 112, 154, 0.7)',
                        'rgba(255, 5, 124, 0.7)',
                        'rgba(79, 172, 254, 0.7)',
                        'rgba(141, 11, 147, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: textColor,
                            font: {
                                family: fontFamily,
                                size: 11
                            }
                        }
                    }
                }
            }
        });

        // Depth vs Pointers Chart
        const depthPointersCtx = document.getElementById('depthPointersChart').getContext('2d');
        if (dashboardData.depth_pointers_data && dashboardData.depth_pointers_data.length > 0) {
            chartInstances.depthPointersChart = new Chart(depthPointersCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Files',
                        data: dashboardData.depth_pointers_data,
                        backgroundColor: 'rgba(103, 126, 234, 0.7)',
                        borderColor: 'rgba(103, 126, 234, 1)',
                        borderWidth: 1,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Block Depth',
                                color: textColor,
                                font: {
                                    family: fontFamily,
                                    size: 12
                                }
                            },
                            grid: { 
                                color: gridColor 
                            },
                            ticks: { 
                                color: textColor,
                                font: {
                                    family: fontFamily,
                                    size: 11
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Pointer Operations',
                                color: textColor,
                                font: {
                                    family: fontFamily,
                                    size: 12
                                }
                            },
                            grid: { 
                                color: gridColor 
                            },
                            ticks: { 
                                color: textColor,
                                font: {
                                    family: fontFamily,
                                    size: 11
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: textColor,
                                font: {
                                    family: fontFamily,
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'File: ' + context.raw.file;
                                },
                                afterLabel: function(context) {
                                    return 'Depth: ' + context.raw.y + '\\nPointers: ' + context.raw.x;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    function initAdvancedCharts() {
        // Advanced charts initialization when needed
        console.log('Advanced charts initialized');
    }
    </script>
</body>
</html>'''