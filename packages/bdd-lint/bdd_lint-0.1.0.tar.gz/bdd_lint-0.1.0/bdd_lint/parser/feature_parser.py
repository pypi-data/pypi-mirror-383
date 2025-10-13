def parse_feature_file(file_path):
    scenarios = []
    feature_name = ''
    feature_tags = []
    current_tags = []
    current_scenario = None
    background_steps = []
    examples = []
    scenario_outline = False
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('Feature:'):
            feature_name = line
            # Check for tags above feature
            if i > 0 and lines[i-1].strip().startswith('@'):
                feature_tags = [tag.strip() for tag in lines[i-1].strip().split() if tag.startswith('@')]
        elif line.startswith('@'):
            current_tags = [tag.strip() for tag in line.split() if tag.startswith('@')]
        elif line.startswith('Background:'):
            background_steps = []
            # Collect background steps
            for j in range(i+1, len(lines)):
                step_line = lines[j].strip()
                if step_line.startswith(('Given', 'When', 'Then', 'And', 'But')):
                    background_steps.append(step_line)
                else:
                    break
        elif line.startswith('Scenario Outline:'):
            if current_scenario:
                scenarios.append(current_scenario)
            current_scenario = {
                'name': line,
                'steps': [],
                'tags': current_tags,
                'feature_name': feature_name,
                'feature_tags': feature_tags,
                'background_steps': background_steps,
                'examples': [],
                'scenario_outline': True
            }
            current_tags = []
            scenario_outline = True
        elif line.startswith('Scenario:'):
            if current_scenario:
                scenarios.append(current_scenario)
            current_scenario = {
                'name': line,
                'steps': [],
                'tags': current_tags,
                'feature_name': feature_name,
                'feature_tags': feature_tags,
                'background_steps': background_steps,
                'examples': [],
                'scenario_outline': False
            }
            current_tags = []
            scenario_outline = False
        elif line.startswith('Examples:') and current_scenario:
            # Collect examples table
            examples = []
            for j in range(i+1, len(lines)):
                ex_line = lines[j].strip()
                if ex_line and not ex_line.startswith(('Scenario', 'Scenario Outline', 'Feature:', '@', 'Background:')):
                    examples.append(ex_line)
                else:
                    break
            current_scenario['examples'] = examples
        elif line.startswith(('Given', 'When', 'Then', 'And', 'But')) and current_scenario:
            current_scenario['steps'].append(line)
    if current_scenario:
        scenarios.append(current_scenario)
    return scenarios