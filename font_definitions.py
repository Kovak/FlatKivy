font_styles = {
	'Display 4': {
		'font': 'Roboto-Light.ttf', 
		'sizings': {'mobile': (112, 'sp'), 'desktop': (112, 'sp')},
		'alpha': .54,
		'wrap': False,
		}, 
	'Display 3': {
		'font': 'Roboto-Regular.ttf', 
		'sizings': {'mobile': (56, 'sp'), 'desktop': (56, 'sp')},
		'alpha': .54,
		'wrap': False,
		},
	'Display 2': {
		'font': 'Roboto-Regular.ttf', 
		'sizings': {'mobile': (45, 'sp'), 'desktop': (45, 'sp')},
		'alpha': .54,
		'wrap': True,
		'wrap_id': '1',
		'leading': (48, 'pt'),
		},
	'Display 1': {
		'font': 'Roboto-Regular.ttf', 
		'sizings': {'mobile': (34, 'sp'), 'desktop': (34, 'sp')},
		'alpha': .54,
		'wrap': True,
		'wrap_id': '2',
		'leading': (40, 'pt'),
		},
	'Headline': {
		'font': 'Roboto-Regular.ttf', 
		'sizings': {'mobile': (24, 'sp'), 'desktop': (24, 'sp')},
		'alpha': .87,
		'wrap': True,
		'wrap_id': '3',
		'leading': (32, 'pt'),
		},
	'Title': {
		'font': 'Roboto-Medium.ttf', 
		'sizings': {'mobile': (20, 'sp'), 'desktop': (20, 'sp')},
		'alpha': .87,
		'wrap': False,
		},
	'Subhead': {
		'font': 'Roboto-Regular.ttf', 
		'sizings': {'mobile': (16, 'sp'), 'desktop': (15, 'sp')},
		'alpha': .87,
		'wrap': True,
		'wrap_id': '4',
		'leading': (28, 'pt'),
		},
	'Body 2': {
		'font': 'Roboto-Medium.ttf', 
		'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
		'alpha': .87,
		'wrap': True,
		'wrap_id': '5',
		'leading': (24, 'pt'),
		},
	'Body 1': {
		'font': 'Roboto-Regular.ttf', 
		'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
		'alpha': .87,
		'wrap': True,
		'wrap_id': '6',
		'leading': (20, 'pt'),
		},
	'Caption': {
		'font': 'Roboto-Regular.ttf', 
		'sizings': {'mobile': (12, 'sp'), 'desktop': (12, 'sp')},
		'alpha': .54,
		'wrap': False,
		},
	'Menu': {
		'font': 'Roboto-Medium.ttf', 
		'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
		'alpha': .87,
		'wrap': False,
		},
	'Button': {
		'font': 'Roboto-Medium.ttf', 
		'sizings': {'mobile': (14, 'sp'), 'desktop': (14, 'sp')},
		'alpha': .87,
		'wrap': False,
		},
	}

wrap_ids = {}


for each in font_styles:
	entry = font_styles[each]
	if entry['wrap']:
		wrap_ids[entry['wrap_id']] = each


