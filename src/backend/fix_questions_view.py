import re

path = r"F:\CodexWorkspace\Project004_考试系统\src\frontend\src\views\QuestionsView.vue"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Change dialog width 
content = content.replace('width="680px"', 'width="900px"')

# Fix 2: Make top fields two-column
# Replace the flat form items with el-row/el-col layout
old_pattern = r'(<el-form-item label="科目" required>.*?</el-form-item>\s*<el-form-item label="章节">.*?</el-form-item>\s*<el-form-item label="题型" required>.*?</el-form-item>\s*.*?<el-form-item label="难度">.*?</el-form-item>\s*<el-form-item label="专项">.*?</el-form-item>)'

# Simpler: just wrap the top 5 form items in rows/cols
old_top = '''            <el-form-item label="科目" required>'''
new_top = '''          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="科目" required>'''

content = content.replace(old_top, new_top, 1)

# Now find <el-form-item label="专项"> and close the col/row after it
# Find the specialty form-item end
specialty_end = content.find('<el-form-item label="专项">')
if specialty_end > 0:
    # Find the closing </el-form-item> after specialty
    close_pos = content.find('</el-form-item>', specialty_end)
    if close_pos > 0:
        end = close_pos + len('</el-form-item>')
        content = content[:end] + '\n            </el-col>\n          </el-row>' + content[end:]

# Fix 3: Wrap subject+chapter in one row, type+difficulty+specialty in another
# This is getting complex. Let me just do a simpler approach.

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed dialog width and started layout")
