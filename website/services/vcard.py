"""Serialize the ContactPage singleton as a vCard 3.0 (RFC 2426) file.

3.0 rather than 4.0 because it is the version iOS and Android contact import
have supported longest. Lines end in CRLF and fold at 75 octets, per the RFC.
"""

MAX_LINE_OCTETS = 75


def _escape(value):
    """Escape a TEXT value; order matters, backslashes must go first."""
    return (
        value.replace('\\', '\\\\')
        .replace(',', '\\,')
        .replace(';', '\\;')
        .replace('\r\n', '\\n')
        .replace('\n', '\\n')
    )


def _fold(line):
    """Fold to 75 octets without splitting a multi-byte UTF-8 character."""
    lines = []
    current = ''
    current_octets = 0
    for char in line:
        char_octets = len(char.encode('utf-8'))
        if current_octets + char_octets > MAX_LINE_OCTETS:
            lines.append(current)
            current = ' '  # The leading space marks a continuation line.
            current_octets = 1
        current += char
        current_octets += char_octets
    lines.append(current)
    return '\r\n'.join(lines)


def build_vcard(contact):
    """Return the vCard text for a ContactPage instance."""
    name = ';'.join(
        _escape(part)
        for part in (contact.last_name, contact.first_name, contact.middle_name, '', '')
    )
    lines = [
        'BEGIN:VCARD',
        'VERSION:3.0',
        f'N:{name}',
        f'FN:{_escape(contact.full_name)}',
        f'ORG:{_escape(contact.organization)}',
        f'TITLE:{_escape(contact.job_title)}',
        f'EMAIL;TYPE=INTERNET;TYPE=WORK:{contact.email}',
        f'TEL;TYPE=CELL;TYPE=VOICE:{contact.cell_phone}',
        f'URL:{contact.CANONICAL_URL}',
        'END:VCARD',
    ]
    return ''.join(f'{_fold(line)}\r\n' for line in lines)
