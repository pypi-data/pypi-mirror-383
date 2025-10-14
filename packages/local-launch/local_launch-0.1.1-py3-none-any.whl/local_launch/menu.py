from questionary import prompt, Separator

def main_menu():
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'Select an action:',
            'choices': [
                'Kafka Actions',
                'Change Project Root Directory and Setup',
                'Change Context to Kind Cluster',
                Separator(),
                'Exit Tool'
            ]
        }
    ]
    answers = prompt(questions)
    return answers['action']

def kafka_menu():
    questions = [
        {
            'type': 'list',
            'name': 'kafka_action',
            'message': 'Select a Kafka action:',
            'choices': [
                'Create Topic',
                'Delete Topic',
                'Produce Message',
                'Consume Message',
                Separator(),
                'Back to Main Menu'
            ]
        }
    ]
    answers = prompt(questions)
    return answers['kafka_action']

def project_config_menu():
    questions = [
        {
            'type': 'list',
            'name': 'config_action',
            'message': 'Select a configuration action:',
            'choices': [
                'View Current Configuration',
                'Edit Configuration',
                Separator(),
                'Back to Main Menu'
            ]
        }
    ]
    answers = prompt(questions)
    return answers['config_action']

def exit_menu():
    questions = [
        {
            'type': 'list',
            'name': 'exit_action',
            'message': 'Select an exit option:',
            'choices': [
                'Exit Tool Without Deleting Cluster',
                'Exit With Deleting Cluster',
                Separator(),
                'Back to Main Menu'
            ]
        }
    ]
    answers = prompt(questions)
    return answers['exit_action']