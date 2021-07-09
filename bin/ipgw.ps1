$env:PYTHONPATH = (get-item $PSScriptRoot).parent.FullName
$env:executeable_path = Join-Path -Path $env:PYTHONPATH -ChildPath "cli\action.py"
python $env:executeable_path $args