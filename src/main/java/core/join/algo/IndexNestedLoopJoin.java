package core.join.algo;

import core.adapt.AccessMethod;
import core.join.HPJoinInput;
import core.join.PartitionRange;
import core.utils.Range;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.InputSplit;

import java.util.ArrayList;
import java.util.List;

public class IndexNestedLoopJoin extends JoinAlgo {

	HPJoinInput joinInput1;
	HPJoinInput joinInput2;

	public IndexNestedLoopJoin(HPJoinInput joinInput1, HPJoinInput joinInput2) {
		this.joinInput1 = joinInput1;
		this.joinInput2 = joinInput2;
	}

	@Override
	public List<InputSplit> getSplits() {
		List<InputSplit> finalSplits = new ArrayList<InputSplit>();
		List<Range> ranges = joinInput2.getRangeSplits(SPLIT_FANOUT, false);
		for (Range r : ranges) {
			// ids from smaller table that match this range of values
			AccessMethod.PartitionSplit[] splits1 = joinInput1.getRangeScan(
					true, r.getLow(), r.getHigh());
			AccessMethod.PartitionSplit[] splits2 = joinInput2.getRangeScan(
					true, r.getLow(), r.getHigh());

			Path[] input1Paths = joinInput1.getPaths(splits1);
			Path[] input2Paths = joinInput2.getPaths(splits2);
			System.out.println("number of files from the smaller input: "
					+ input1Paths.length);
			System.out.println("number of files from the larger input: "
					+ input2Paths.length);

			long[] input1Lengths = joinInput1.getLengths(splits1);
			long[] input2Lengths = joinInput2.getLengths(splits2);

			InputSplit thissplit = formSplit(input1Paths, input2Paths,
					input1Lengths, input2Lengths);
			finalSplits.add(thissplit);
		}
		return finalSplits;
	}
}