import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';

class StudentAuditResults extends StatefulWidget {
  const StudentAuditResults({super.key});

  @override
  State<StudentAuditResults> createState() => _StudentAuditResultsState();
}

class _StudentAuditResultsState extends State<StudentAuditResults> {
  final ApiService _api = ApiService();
  List<dynamic> _results = [];
  bool _loading = true;
  String? _error;
  String? _expandedId;
  Map<String, dynamic>? _detail;
  bool _detailLoading = false;

  @override
  void initState() {
    super.initState();
    _loadResults();
  }

  Future<void> _loadResults() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await _api.getStudentAuditResults(limit: 50);
      if (!mounted) return;
      setState(() {
        _results = data['results'] ?? [];
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _toggleExpand(String id) async {
    if (_expandedId == id) {
      setState(() {
        _expandedId = null;
        _detail = null;
      });
      return;
    }

    setState(() {
      _expandedId = id;
      _detailLoading = true;
      _detail = null;
    });

    try {
      final data = await _api.getStudentAuditResultById(id);
      if (!mounted) return;
      setState(() => _detail = data);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load details: $e')),
      );
    } finally {
      if (mounted) setState(() => _detailLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Audit Results'),
        backgroundColor: const Color(0xFF1E3A5F),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await context.read<AuthProvider>().logout();
              if (mounted) {
                Navigator.pushReplacementNamed(context, '/');
              }
            },
            tooltip: 'Logout',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(_error!, style: const TextStyle(color: Colors.red)),
                      const SizedBox(height: 16),
                      ElevatedButton(
                          onPressed: _loadResults, child: const Text('Retry')),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadResults,
                  child: _results.isEmpty
                      ? ListView(
                          children: [
                            const SizedBox(height: 100),
                            Center(
                              child: Column(
                                children: [
                                  Icon(Icons.assignment_outlined,
                                      size: 64, color: Colors.grey[400]),
                                  const SizedBox(height: 16),
                                  Text('No audit results available yet.',
                                      style:
                                          TextStyle(color: Colors.grey[600])),
                                  const SizedBox(height: 8),
                                  Text(
                                      'Your administrator will upload your results here.',
                                      style:
                                          TextStyle(color: Colors.grey[400])),
                                ],
                              ),
                            ),
                          ],
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _results.length,
                          itemBuilder: (context, index) {
                            final result = _results[index];
                            return _buildResultCard(result);
                          },
                        ),
                ),
    );
  }

  Widget _buildResultCard(dynamic result) {
    final isEligible = result['eligible'] == true;
    final isExpanded = _expandedId == result['id'];

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Column(
        children: [
          // Header
          InkWell(
            onTap: () => _toggleExpand(result['id']),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor:
                        isEligible ? Colors.green.shade50 : Colors.red.shade50,
                    child: Icon(
                      isEligible ? Icons.check_circle : Icons.cancel,
                      color: isEligible ? Colors.green : Colors.red,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${result['program']} — Level ${result['audit_level']}',
                          style: const TextStyle(
                              fontWeight: FontWeight.w600, fontSize: 15),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _formatDate(result['created_at']),
                          style:
                              TextStyle(color: Colors.grey[500], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  Chip(
                    label: Text(
                      isEligible ? 'Eligible' : 'Not Eligible',
                      style: const TextStyle(fontSize: 12),
                    ),
                    backgroundColor:
                        isEligible ? Colors.green.shade50 : Colors.red.shade50,
                  ),
                  Icon(
                    isExpanded ? Icons.expand_less : Icons.expand_more,
                    color: Colors.grey,
                  ),
                ],
              ),
            ),
          ),

          // Expanded detail
          if (isExpanded) _buildDetailSection(result, isEligible),
        ],
      ),
    );
  }

  Widget _buildDetailSection(dynamic result, bool isEligible) {
    return Container(
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: Colors.grey.shade200)),
      ),
      padding: const EdgeInsets.all(16),
      child: _detailLoading
          ? const Center(child: CircularProgressIndicator())
          : _detail == null
              ? const Text('Failed to load details')
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Status banner
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: isEligible
                            ? Colors.green.shade50
                            : Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: isEligible
                              ? Colors.green.shade200
                              : Colors.red.shade200,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            isEligible ? Icons.check_circle : Icons.cancel,
                            color: isEligible ? Colors.green : Colors.red,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            isEligible
                                ? 'You are eligible for graduation!'
                                : 'You are not yet eligible',
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              color: isEligible
                                  ? Colors.green.shade700
                                  : Colors.red.shade700,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Result text
                    if (_detail!['result_text'] != null) ...[
                      const Text('Detailed Report',
                          style: TextStyle(fontWeight: FontWeight.w600)),
                      const SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: SelectableText(
                          _detail!['result_text'],
                          style: const TextStyle(
                              fontFamily: 'monospace', fontSize: 12),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Result JSON summary
                    if (_detail!['result_json'] != null) ...[
                      const Text('Summary',
                          style: TextStyle(fontWeight: FontWeight.w600)),
                      const SizedBox(height: 8),
                      ..._buildSummaryRows(_detail!['result_json']),
                    ],

                    // Request button for failed results
                    if (!isEligible) ...[
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton.icon(
                          onPressed: () => _showRequestDialog(result['id']),
                          icon: const Icon(Icons.send),
                          label: const Text(
                              'Submit Review Request for This Result'),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.orange,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
    );
  }

  List<Widget> _buildSummaryRows(Map<String, dynamic> json) {
    final entries =
        json.entries.where((e) => e.value is! Map && e.value is! List).take(10);
    return entries.map((e) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              e.key.replaceAll('_', ' ').toUpperCase(),
              style: TextStyle(color: Colors.grey[600], fontSize: 13),
            ),
            Text(
              '${e.value}',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ],
        ),
      );
    }).toList();
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return dateStr;
    }
  }

  void _showRequestDialog(String auditResultId) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Submit Review Request'),
        content: TextField(
          controller: controller,
          maxLines: 4,
          decoration: const InputDecoration(
            hintText: 'Describe your concern (min 10 characters)...',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (controller.text.trim().length < 10) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Message must be at least 10 characters')),
                );
                return;
              }
              try {
                await _api.submitStudentRequest(
                  message: controller.text,
                  auditResultId: auditResultId,
                );
                if (mounted) {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                        content: Text('Request submitted successfully')),
                  );
                }
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Failed: $e')),
                );
              }
            },
            child: const Text('Submit'),
          ),
        ],
      ),
    );
  }
}
