"""Fix CertificatesView.vue - error handling for applyPractice"""
path = r'F:\CodexWorkspace\Project004_考试系统\src\frontend\src\views\CertificatesView.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''async function applyPractice(item) {
  try {
    await ElMessageBox.confirm('\u786e\u8ba4\u7533\u8bf7\u300c' + item.certificate_name + '\u300d\uff1f', '\u7533\u8bf7\u7ec3\u4e60\u8bc1\u4e66')
    await api.post('/certificates/apply', null, { params: { certificate_id: item.certificate_id } })
    ElMessage.success('\u8bc1\u4e66\u7533\u8bf7\u6210\u529f\uff01')
    const [my, eligibility] = await Promise.all([
      api.get('/certificates/my'),
      api.get('/certificates/practice-eligibility'),
    ])
    myCerts.value = my.data || []; practiceEligible.value = eligibility.data || []
  } catch {}
}'''

new = '''async function applyPractice(item) {
  try {
    await ElMessageBox.confirm('\u786e\u8ba4\u7533\u8bf7\u300c' + item.certificate_name + '\u300d\uff1f', '\u7533\u8bf7\u7ec3\u4e60\u8bc1\u4e66')
  } catch { return }
  try {
    await api.post('/certificates/apply', null, { params: { certificate_id: item.certificate_id } })
    ElMessage.success('\u8bc1\u4e66\u7533\u8bf7\u6210\u529f\uff01')
    const [my, eligibility] = await Promise.all([
      api.get('/certificates/my'),
      api.get('/certificates/practice-eligibility'),
    ])
    myCerts.value = my.data || []; practiceEligible.value = eligibility.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '\u7533\u8bf7\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5')
  }
}'''

if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed applyPractice error handling')
else:
    print('ERROR: Could not find old applyPractice')
    # Debug: find the function
    idx = content.find('async function applyPractice')
    if idx >= 0:
        snippet = content[idx:idx+500]
        print('Found at index', idx)
        print(repr(snippet[:300]))
