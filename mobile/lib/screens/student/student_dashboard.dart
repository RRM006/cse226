import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../widgets/stat_card.dart';

class StudentDashboard extends StatefulWidget {
  const StudentDashboard({super.key});

  @override
  State<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends State<StudentDashboard> {
  final ApiService _api = ApiService();
  bool _loading = true;
  String? _error;
  List<dynamic> _results = [];
  List<dynamic> _requests = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final resultsRes = await _api.getStudentAuditResults();
      final requestsRes = await _api.getStudentRequests();
      if (!mounted) return;
      setState(() {
        _results = resultsRes['results'] ?? [];
        _requests = requestsRes['requests'] ?? [];
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final eligibleCount = _results.where((r) => r['eligible'] == true).length;
    final failedCount = _results.where((r) => r['eligible'] != true).length;
    final pendingCount =
        _requests.where((r) => r['status'] == 'pending').length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Dashboard'),
        backgroundColor: const Color(0xFF1E3A5F),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pushReplacementNamed(context, '/'),
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
                          onPressed: _loadData, child: const Text('Retry')),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Stats Row
                        Row(
                          children: [
                            Expanded(
                              child: StatCard(
                                label: 'Audits',
                                value: _results.length,
                                icon: Icons.assignment,
                                color: Colors.blue,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: StatCard(
                                label: 'Eligible',
                                value: eligibleCount,
                                icon: Icons.check_circle,
                                color: Colors.green,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: StatCard(
                                label: 'Not Eligible',
                                value: failedCount,
                                icon: Icons.cancel,
                                color: Colors.red,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: StatCard(
                                label: 'Pending',
                                value: pendingCount,
                                icon: Icons.schedule,
                                color: Colors.orange,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),

                        // Latest Results
                        const Text(
                          'Latest Audit Results',
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 12),
                        if (_results.isEmpty)
                          _buildEmptyCard('No audit results yet.',
                              'Your admin will upload your results.')
                        else
                          ..._results
                              .take(3)
                              .map((result) => _buildResultCard(result)),

                        const SizedBox(height: 24),

                        // Submit Request Button
                        if (failedCount > 0)
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              onPressed: () => _showRequestDialog(),
                              icon: const Icon(Icons.send),
                              label: const Text('Submit Review Request'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: Colors.orange,
                                padding:
                                    const EdgeInsets.symmetric(vertical: 14),
                              ),
                            ),
                          ),

                        const SizedBox(height: 24),

                        // Recent Requests
                        const Text(
                          'Recent Requests',
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 12),
                        if (_requests.isEmpty)
                          _buildEmptyCard('No requests submitted yet.',
                              'Click the button above to submit a request.')
                        else
                          ..._requests
                              .take(5)
                              .map((req) => _buildRequestCard(req)),

                        // Navigate to full lists
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () => Navigator.pushNamed(
                                    context, '/student/audit-results'),
                                icon: const Icon(Icons.list),
                                label: const Text('All Results'),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () => Navigator.pushNamed(
                                    context, '/student/requests'),
                                icon: const Icon(Icons.mail),
                                label: const Text('All Requests'),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildEmptyCard(String title, String subtitle) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(Icons.inbox, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 12),
            Text(title, style: TextStyle(color: Colors.grey[600])),
            const SizedBox(height: 4),
            Text(subtitle,
                style: TextStyle(color: Colors.grey[400], fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard(dynamic result) {
    final isEligible = result['eligible'] == true;
    return Card(
      child: ListTile(
        leading: Icon(
          isEligible ? Icons.check_circle : Icons.cancel,
          color: isEligible ? Colors.green : Colors.red,
        ),
        title: Text('${result['program']} - Level ${result['audit_level']}'),
        subtitle: Text(_formatDate(result['created_at'])),
        trailing: Chip(
          label: Text(
            isEligible ? 'Eligible' : 'Not Eligible',
            style: const TextStyle(fontSize: 12),
          ),
          backgroundColor:
              isEligible ? Colors.green.shade50 : Colors.red.shade50,
        ),
        onTap: () => Navigator.pushNamed(context, '/student/audit-results'),
      ),
    );
  }

  Widget _buildRequestCard(dynamic req) {
    final status = req['status'] ?? 'pending';
    return Card(
      child: ListTile(
        title: Text(
          req['message'] ?? '',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(_formatDate(req['created_at'])),
        trailing: Chip(
          label: Text(status, style: const TextStyle(fontSize: 12)),
          backgroundColor: _statusColor(status),
        ),
      ),
    );
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'approved':
        return Colors.green.shade50;
      case 'rejected':
        return Colors.red.shade50;
      case 'reviewed':
        return Colors.blue.shade50;
      default:
        return Colors.orange.shade50;
    }
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}/${date.year}';
    } catch (_) {
      return dateStr;
    }
  }

  void _showRequestDialog() {
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
                await _api.submitStudentRequest(message: controller.text);
                if (mounted) {
                  Navigator.pop(ctx);
                  _loadData();
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
